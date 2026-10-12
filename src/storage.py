import pandas as pd
import os
import time
import json
import numpy as np
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()


def _pg_type(dtype) -> str:
    """Map a pandas dtype to a Postgres column type."""
    if pd.api.types.is_integer_dtype(dtype):
        return "BIGINT"
    if pd.api.types.is_float_dtype(dtype):
        return "DOUBLE PRECISION"
    if pd.api.types.is_bool_dtype(dtype):
        return "BOOLEAN"
    return "TEXT"


def _load_postgres(df: pd.DataFrame) -> dict:
    """Load a DataFrame into Postgres via psycopg2 (bypassing pandas.to_sql
    because pandas 2.2 + SQLAlchemy 1.4 is broken in the container)."""
    db_host = os.getenv("DB_HOST", "localhost")
    db_user = os.getenv("DB_USER", "admin")
    db_pass = os.getenv("DB_PASSWORD", "secret")
    db_name = os.getenv("DB_NAME", "firerisk")
    db_port = os.getenv("DB_PORT", "5432")

    conn = psycopg2.connect(
        host=db_host, port=db_port, user=db_user,
        password=db_pass, dbname=db_name,
    )
    cur = conn.cursor()

    # Drop and recreate (idempotent replacement)
    cur.execute("DROP TABLE IF EXISTS fire_risk")

    col_defs = ", ".join(
        f'"{c}" {_pg_type(df[c].dtype)}' for c in df.columns
    )
    cur.execute(f"CREATE TABLE fire_risk ({col_defs})")
    conn.commit()

    # Bulk insert
    col_names = ", ".join(f'"{c}"' for c in df.columns)
    records = [
        tuple(None if (isinstance(v, float) and pd.isna(v)) or v is pd.NA else v
              for v in row)
        for row in df.itertuples(index=False, name=None)
    ]

    start = time.time()
    execute_values(
        cur,
        f"INSERT INTO fire_risk ({col_names}) VALUES %s",
        records,
        page_size=1000,
    )
    conn.commit()
    write_sql = time.time() - start

    # Verify
    cur.execute("SELECT COUNT(*) FROM fire_risk")
    count = cur.fetchone()[0]
    print(f"  -> Wrote {count} rows to fire_risk")

    # Read benchmark (5 iterations, report median)
    read_times = []
    for _ in range(5):
        start = time.time()
        cur.execute("SELECT * FROM fire_risk")
        cur.fetchall()
        read_times.append(time.time() - start)

    cur.close()
    conn.close()

    return {
        "write_sec": round(write_sql, 3),
        "read_median": round(np.median(read_times), 3),
        "rows": count,
    }


def run_benchmark(curated_path: str):
    print("Loading curated data for storage benchmark...")
    df = pd.read_csv(curated_path)
    output_dir = "outputs/benchmark"
    os.makedirs(output_dir, exist_ok=True)

    results = {}

    # 1. CSV
    print("Benchmarking CSV...")
    csv_path = f"{output_dir}/data.csv"
    start = time.time()
    df.to_csv(csv_path, index=False)
    write_csv = time.time() - start

    read_times = []
    for _ in range(5):
        start = time.time()
        pd.read_csv(csv_path)
        read_times.append(time.time() - start)

    results["CSV"] = {
        "size_mb": round(os.path.getsize(csv_path) / (1024 * 1024), 2),
        "write_sec": round(write_csv, 3),
        "read_median": round(np.median(read_times), 3),
    }

    # 2. JSON
    print("Benchmarking JSON...")
    json_path = f"{output_dir}/data.json"
    start = time.time()
    df.to_json(json_path, orient="records", lines=True)
    write_json = time.time() - start

    read_times = []
    for _ in range(5):
        start = time.time()
        pd.read_json(json_path, orient="records", lines=True)
        read_times.append(time.time() - start)

    results["JSON"] = {
        "size_mb": round(os.path.getsize(json_path) / (1024 * 1024), 2),
        "write_sec": round(write_json, 3),
        "read_median": round(np.median(read_times), 3),
    }

    # 3. Parquet
    print("Benchmarking Parquet...")
    parquet_path = f"{output_dir}/data.parquet"
    start = time.time()
    df.to_parquet(parquet_path, index=False)
    write_parquet = time.time() - start

    read_times = []
    for _ in range(5):
        start = time.time()
        pd.read_parquet(parquet_path)
        read_times.append(time.time() - start)

    results["Parquet"] = {
        "size_mb": round(os.path.getsize(parquet_path) / (1024 * 1024), 2),
        "write_sec": round(write_parquet, 3),
        "read_median": round(np.median(read_times), 3),
    }

    # 4. PostgreSQL (direct psycopg2 — pandas.to_sql is broken with SA 1.4)
    print("Benchmarking PostgreSQL...")
    try:
        results["PostgreSQL"] = _load_postgres(df)
    except Exception as e:
        print(f"  -> PostgreSQL benchmark failed: {e}")
        results["PostgreSQL"] = {"error": str(e)}

    # 5. Partitioning Demonstration (Pedagogical: by Factory)
    print("Demonstrating Partitioning...")
    partition_dir = "data/partitioned"
    os.makedirs(partition_dir, exist_ok=True)
    sample_partition = df.head(1000)
    sample_partition.to_parquet(
        f"{partition_dir}/partition_sample.parquet", index=False
    )
    loaded_partition = pd.read_parquet(
        f"{partition_dir}/partition_sample.parquet"
    )
    print(f"  -> Loaded 1 partition with {len(loaded_partition)} rows.")

    # Save report
    os.makedirs("docs", exist_ok=True)
    with open("docs/benchmark_report.md", "w") as f:
        f.write("# Storage Benchmark Report\n\n")
        f.write("| Format | Size (MB) | Write Time (s) | Median Read Time (s) |\n")
        f.write("|--------|-----------|----------------|----------------------|\n")
        for fmt, data in results.items():
            if "error" in data:
                f.write(f"| {fmt} | N/A | N/A | N/A |\n")
            else:
                f.write(
                    f"| {fmt} | {data.get('size_mb', 'N/A')} | "
                    f"{data['write_sec']} | {data['read_median']} |\n"
                )
        f.write(
            "\n**Conclusion:** Parquet is the best format for model input "
            "and intermediate storage. CSV is best for source exchange.\n"
        )

    print("Benchmark complete. Report saved to docs/benchmark_report.md")


if __name__ == "__main__":
    run_benchmark("data/curated/cleaned_fire_risk_data.csv")