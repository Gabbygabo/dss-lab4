import pytest
import pandas as pd
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ingest import get_file_checksum
from src.validate import validate_data

# --- UNIT TESTS ---
def test_checksum_generation():
    """Unit Test 1: Test that checksum generates a string."""
    checksum = get_file_checksum("data/source/industrial_fire_risk_data.csv")
    assert isinstance(checksum, str)
    assert len(checksum) == 64  # SHA-256 length

def test_validate_data_passes():
    """Unit Test 2: Test that validate_data passes on clean data."""
    try:
        validate_data("data/curated/cleaned_fire_risk_data.csv")
    except SystemExit as e:
        assert e.code == 0

def test_validate_data_fails_on_missing_column():
    """Unit Test 3: Test that validate_data fails if a column is missing."""
    df = pd.read_csv("data/curated/cleaned_fire_risk_data.csv")
    df = df.drop(columns=['Temp'])
    df.to_csv("data/curated/test_temp.csv", index=False)
    with pytest.raises(SystemExit) as e:
        validate_data("data/curated/test_temp.csv")
    assert e.value.code == 1
    os.remove("data/curated/test_temp.csv")

# --- INTEGRATION TESTS ---
def test_ingest_to_transform_integration():
    """Integration Test 1: Ingest output can be read by transform logic."""
    # This assumes the pipeline has been run at least once
    assert os.path.exists("data/raw/batch_1.csv")
    df_raw = pd.read_csv("data/raw/batch_1.csv")
    assert len(df_raw) > 0

def test_train_to_output_integration():
    """Integration Test 2: Training produces metrics.json and predictions.csv."""
    assert os.path.exists("outputs/metrics.json")
    assert os.path.exists("outputs/predictions.csv")
    df_pred = pd.read_csv("outputs/predictions.csv")
    assert 'Actual' in df_pred.columns
    assert 'Predicted' in df_pred.columns