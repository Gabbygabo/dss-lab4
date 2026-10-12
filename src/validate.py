import pandas as pd
import sys
import os

def validate_data(file_path, stage="raw"):
    print(f"Running Data Quality Checks on {stage} data: {file_path}")
    df = pd.read_csv(file_path)
    errors = []

    # 1. Schema Check
    required_cols = ['Temp', 'Pressure', 'Risk', 'Workers']
    for col in required_cols:
        if col not in df.columns:
            errors.append(f"Schema Error: Missing column {col}")

    # 2. Completeness (Null Check)
    if df['Risk'].isnull().sum() > 0:
        errors.append("Completeness Error: Risk column has null values.")

    # 3. Uniqueness (Duplicate Check)
    if df.duplicated().sum() > 0:
        errors.append(f"Uniqueness Error: Found {df.duplicated().sum()} duplicate rows.")

    # 4. Validity (Range Check)
    if 'Risk' in df.columns:
        if df['Risk'].min() < 0 or df['Risk'].max() > 100:
            errors.append("Validity Error: Risk values outside 0-100 range.")

    # 5. Project-Specific Rule (No target leakage)
    if 'Accident' in df.columns:
        errors.append("Leakage Error: Accident column is present in model-ready data.")

    if errors:
        print("VALIDATION FAILED:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("VALIDATION PASSED: All data quality checks passed.")

if __name__ == "__main__":
    # Check command line argument for stage
    stage = "raw" if "--stage" not in sys.argv else sys.argv[sys.argv.index("--stage") + 1]
    path = "data/raw/batch_1.csv" if stage == "raw" else "data/curated/cleaned_fire_risk_data.csv"
    validate_data(path, stage)