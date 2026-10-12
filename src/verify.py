import pandas as pd
import glob

def verify_pipeline(raw_dir: str, curated_path: str):
    print("\n" + "="*50)
    print("FINAL DUPLICATE & ROW-COUNT VERIFICATION")
    print("="*50)

    # 1. Verify Raw Batches
    batch_files = glob.glob(f"{raw_dir}batch_*.csv")
    raw_df = pd.concat([pd.read_csv(f) for f in batch_files], ignore_index=True)
    raw_rows = len(raw_df)
    raw_duplicates = raw_df.duplicated().sum()
    
    print(f"Raw Batches ({len(batch_files)} files combined):")
    print(f"  - Total Rows: {raw_rows}")
    print(f"  - Duplicate Rows: {raw_duplicates}")
    print(f"  - Expected Rows: 100,000")

    # 2. Verify Curated Data
    curated_df = pd.read_csv(curated_path)
    curated_rows = len(curated_df)
    curated_duplicates = curated_df.duplicated().sum()
    
    print(f"\nCurated Dataset ({curated_path}):")
    print(f"  - Total Rows: {curated_rows}")
    print(f"  - Duplicate Rows: {curated_duplicates}")
    print(f"  - Expected Rows: 98,000 (after dropping 2,000 missing 'Workers')")

    print("\n" + "="*50)
    if raw_rows == 100000 and raw_duplicates == 0 and curated_rows == 98000 and curated_duplicates == 0:
        print("VERIFICATION PASSED: No duplicates and row counts are correct.")
    else:
        print("VERIFICATION FAILED: Please check the data pipeline.")
    print("="*50)

if __name__ == "__main__":
    verify_pipeline(
        raw_dir="data/raw/", 
        curated_path="data/curated/cleaned_fire_risk_data.csv"
    )