import argparse
import sys
import os
from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingest import ingest_data
from transform import transform_data
from storage import run_benchmark
from train import train_model
from evaluate import compare_metrics

def main():
    parser = argparse.ArgumentParser(description="DSS150P Fire Risk Reproducible Pipeline")
    parser.add_argument(
        "--step", 
        choices=["ingest", "transform", "storage", "train", "evaluate", "validate", "all"], 
        required=True
    )
    parser.add_argument("--force", action="store_true", help="Force full refresh")
    parser.add_argument("--stage", choices=["raw", "curated"], default="raw")
    parser.add_argument("--run-id", default=f"local_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}")
    args = parser.parse_args()

    print(f"Pipeline Run ID: {args.run_id}")

    if args.step in ["ingest", "all"]:
        print("\n" + "="*50); print("STEP 1: INGESTION"); print("="*50)
        ingest_data("data/source/industrial_fire_risk_data.csv", "data/raw/", "metadata/checkpoint.json", force=args.force)

    if args.step in ["transform", "all"]:
        print("\n" + "="*50); print("STEP 2: TRANSFORMATION"); print("="*50)
        transform_data("data/raw/", "data/curated/cleaned_fire_risk_data.csv")
        
    if args.step in ["storage", "all"]:
        print("\n" + "="*50); print("STEP 3: STORAGE BENCHMARK"); print("="*50)
        run_benchmark("data/curated/cleaned_fire_risk_data.csv")
        
    if args.step in ["train", "all"]:
        print("\n" + "="*50); print("STEP 4: MODEL TRAINING"); print("="*50)
        train_model("data/curated/cleaned_fire_risk_data.csv", "outputs/model/", "outputs/metrics.json", "outputs/predictions.csv")

    if args.step in ["evaluate", "all"]:
        print("\n" + "="*50); print("STEP 5: EVALUATION"); print("="*50)
        compare_metrics("outputs/metrics.json", "metadata/expected_metrics.json")

    if args.step in ["validate"]:
        print(f"\nValidating {args.stage} data...")
        from validate import validate_data
        path = "data/raw/batch_1.csv" if args.stage == "raw" else "data/curated/cleaned_fire_risk_data.csv"
        validate_data(path, args.stage)

if __name__ == "__main__":
    main()