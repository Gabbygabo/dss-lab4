import argparse
import sys
import os

# Add the src directory to the Python path so imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingest import ingest_data
from transform import transform_data
from storage import run_benchmark
from train import train_model

def main():
    parser = argparse.ArgumentParser(description="DSS150P Fire Risk Reproducible Pipeline")
    parser.add_argument(
        "--step", 
        choices=["ingest", "transform", "storage", "train", "all"], 
        required=True,
        help="Choose which step of the pipeline to run. Use 'all' to run the entire pipeline."
    )
    parser.add_argument(
        "--force", 
        action="store_true", 
        help="Force full refresh for ingestion, ignoring checkpoints."
    )
    args = parser.parse_args()

    if args.step in ["ingest", "all"]:
        print("\n" + "="*50)
        print("STEP 1: INGESTION")
        print("="*50)
        ingest_data(
            source_path="data/source/industrial_fire_risk_data.csv", 
            raw_dir="data/raw/",
            checkpoint_path="metadata/checkpoint.json",
            force=args.force
        )

    if args.step in ["transform", "all"]:
        print("\n" + "="*50)
        print("STEP 2: TRANSFORMATION")
        print("="*50)
        transform_data(
            input_dir="data/raw/", 
            output_path="data/curated/cleaned_fire_risk_data.csv"
        )
        
    if args.step in ["storage", "all"]:
        print("\n" + "="*50)
        print("STEP 3: STORAGE BENCHMARK")
        print("="*50)
        run_benchmark("data/curated/cleaned_fire_risk_data.csv")
        
    if args.step in ["train", "all"]:
        print("\n" + "="*50)
        print("STEP 4: MODEL TRAINING")
        print("="*50)
        train_model(
            input_path="data/curated/cleaned_fire_risk_data.csv",
            output_dir="outputs/model/",
            metrics_path="outputs/metrics.json",
            predictions_path="outputs/predictions.csv"
        )

if __name__ == "__main__":
    main()