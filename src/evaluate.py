import json
import os

def compare_metrics(actual_path: str, expected_path: str, tolerance: float = 0.01):
    print("Evaluating reproducibility...")
    
    if not os.path.exists(actual_path):
        print(f"Error: {actual_path} not found. Run train.py first.")
        return
        
    with open(actual_path, 'r') as f:
        actual = json.load(f)
        
    with open(expected_path, 'r') as f:
        expected_data = json.load(f)
        
    primary_metric = "RMSE"
    actual_val = actual.get(primary_metric)
    
    # Navigate the nested structure of expected_metrics.json
    expected_val = expected_data.get("reported_metrics", {}).get(primary_metric, 3.24)
    
    diff = abs(actual_val - expected_val)
    
    print(f"Expected {primary_metric}: {expected_val}")
    print(f"Actual {primary_metric}:   {actual_val}")
    print(f"Difference:          {diff:.4f} (Tolerance: {tolerance})")
    
    if diff <= tolerance:
        print("\nREPRODUCIBILITY PASSED: Metrics match within tolerance.")
    else:
        print("\nREPRODUCIBILITY FAILED: Metrics deviate beyond tolerance.")

if __name__ == "__main__":
    compare_metrics("outputs/metrics.json", "metadata/expected_metrics.json")