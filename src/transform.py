import pandas as pd
import glob
import os


def build_staging(input_dir: str, output_dir: str) -> str:
    """Raw batches -> staging layer.

    Responsibilities (per DSS150P Phase II):
      - concat raw batches
      - explicit type conversion
      - null standardization
      - duplicate handling
      - quarantine rejected rows
      - preserve audit columns added by ingest.py
    No business logic, no encoding, no derived features.
    """
    print(f"Building staging from {input_dir}...")

    batch_files = sorted(glob.glob(os.path.join(input_dir, "batch_*.csv")))
    if not batch_files:
        raise FileNotFoundError(f"No batch files found in {input_dir}")

    df = pd.concat([pd.read_csv(f) for f in batch_files], ignore_index=True)
    print(f"Combined {len(batch_files)} batches into {len(df)} rows.")

    # 1. Explicit type conversion
    numeric_cols = ['Risk', 'Workers', 'Temp', 'Pressure', 'Sparks',
                    'Vibration', 'Speed']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 2. Null standardization
    df = df.replace({"": None, "NA": None, "N/A": None, "null": None, "None": None})

    # 3. Quarantine rows missing critical fields
    critical = [c for c in ['Risk', 'Workers'] if c in df.columns]
    if critical:
        bad = df[df[critical].isna().any(axis=1)].copy()
        if not bad.empty:
            os.makedirs("data/quarantine", exist_ok=True)
            bad.to_csv("data/quarantine/rejected_records.csv", index=False)
            print(f"Quarantined {len(bad)} rows -> data/quarantine/rejected_records.csv")
        df = df.dropna(subset=critical)

    # 4. Duplicate handling
    before = len(df)
    df = df.drop_duplicates()
    if len(df) < before:
        print(f"Dropped {before - len(df)} duplicate rows.")

    # 5. Staging audit column (ingest.py already provides pipeline_run_id etc.)
    df['processed_at_utc'] = pd.Timestamp.utcnow().isoformat()
    df['source_row_key'] = range(len(df))

    os.makedirs(output_dir, exist_ok=True)
    staging_path = os.path.join(output_dir, "staging.csv")
    df.to_csv(staging_path, index=False)
    print(f"Staging written: {staging_path} ({len(df)} rows, {len(df.columns)} cols)")
    return staging_path


def build_curated(staging_path: str, output_path: str) -> str:
    """Staging -> curated layer.

    Responsibilities: business rules, derived features, encoding,
    drop leakage columns. Output is exactly what train.py expects.
    """
    print(f"Building curated from {staging_path}...")
    df = pd.read_csv(staging_path)
    print(f"Loaded {len(df)} staging rows.")

    # 1. Data cleaning
    df = df.dropna(subset=['Workers'])

    # 2. Date and time features
    df['DateTime'] = pd.to_datetime(
        df['Date'].astype(str) + ' ' + df['Time'].astype(str),
        format="%d/%m/%Y %H:%M:%S",
        errors="coerce",
    )
    bad_dates = df['DateTime'].isna().sum()
    if bad_dates:
        print(f"WARNING: dropping {bad_dates} rows with unparseable Date/Time.")
        df = df.dropna(subset=['DateTime'])

    df['Hour_of_Day'] = df['DateTime'].dt.hour
    df['Day_of_Week'] = df['DateTime'].dt.dayofweek
    df['Is_Weekend'] = df['Day_of_Week'].isin([5, 6]).astype(int)
    df['Month'] = df['DateTime'].dt.month
    df = df.drop(columns=['Date', 'Time', 'DateTime'])

    # 3. Categorical encoding
    df['Training_Encoded'] = df['Training'].map({'Yes': 1, 'No': 0})
    df['Alarm_Encoded'] = df['Alarm'].map({'On': 1, 'Off': 0})
    df['Exp_Encoded'] = df['Exp'].map({'Junior': 0, 'Senior': 1})
    df = pd.get_dummies(df, columns=['Factory', 'Region', 'Shift'],
                        drop_first=True, dtype=int)
    df = df.drop(columns=['Training', 'Alarm', 'Exp'])

    # 4. Interaction features
    df['Workers_Sparks_Interaction'] = df['Workers'] * df['Sparks']
    df['Temp_Pressure_Interaction'] = df['Temp'] * df['Pressure']
    df['Vibration_Speed_Interaction'] = df['Vibration'] * df['Speed']

    # 5. Drop leakage column
    if 'Accident' in df.columns:
        df = df.drop(columns=['Accident'])

    # 6. Drop audit columns so train.py receives the same shape as before
    audit_cols = ['pipeline_run_id', 'ingested_at_utc', 'source_file',
                  'source_checksum', 'processed_at_utc', 'source_row_key']
    df = df.drop(columns=[c for c in audit_cols if c in df.columns])

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Curated written: {output_path} ({len(df)} rows, {len(df.columns)} cols)")
    return output_path


if __name__ == "__main__":
    staging = build_staging("data/raw/", "data/staging/")
    build_curated(staging, "data/curated/cleaned_fire_risk_data.csv")