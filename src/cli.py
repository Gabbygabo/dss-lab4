import argparse
import sys
import os
import json
import glob
import shutil
from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingest import ingest_data
from transform import build_staging, build_curated
from storage import run_benchmark
from train import train_model
from evaluate import compare_metrics


def step_reproducibility_check(run_id: str) -> None:
    """Compare outputs/metrics.json against metadata/expected_metrics.json
    and write outputs/reproducibility_report.json."""
    expected_path = "metadata/expected_metrics.json"
    actual_path = "outputs/metrics.json"
    report_path = "outputs/reproducibility_report.json"

    with open(expected_path) as f:
        expected = json.load(f)
    with open(actual_path) as f:
        actual = json.load(f)

    tolerance = 0.01
    report = {
        "run_id": run_id,
        "tolerance": tolerance,
        "expected": expected,
        "actual": actual,
        "per_metric": {},
        "pass": True,
    }

    for key in set(expected) | set(actual):
        e = expected.get(key)
        a = actual.get(key)
        if isinstance(e, (int, float)) and isinstance(a, (int, float)):
            diff = abs(e - a)
            passed = diff <= tolerance
            report["per_metric"][key] = {
                "expected": e,
                "actual": a,
                "abs_diff": round(diff, 6),
                "pass": passed,
            }
            if not passed:
                report["pass"] = False

    os.makedirs("outputs", exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Reproducibility report written to {report_path}")
    print(f"Overall pass: {report['pass']}")
    for k, v in report["per_metric"].items():
        status = "OK" if v["pass"] else "FAIL"
        print(f"  {k}: expected={v['expected']} actual={v['actual']} "
              f"diff={v['abs_diff']} [{status}]")

    if not report["pass"]:
        raise SystemExit(f"Reproducibility check failed for run {run_id}")


def _publish_outputs(run_id: str) -> None:
    """Copy final artifacts to outputs/published/ with a run manifest."""
    published = "outputs/published"
    os.makedirs(published, exist_ok=True)

    for fname in ("metrics.json", "predictions.csv", "reproducibility_report.json"):
        src = os.path.join("outputs", fname)
        if os.path.exists(src):
            shutil.copy2(src, published)
            print(f"Copied {src} -> {published}/{fname}")
        else:
            print(f"WARNING: {src} not found, skipping.")

    manifest = {
        "run_id": run_id,
        "published_at_utc": datetime.now(timezone.utc).isoformat(),
        "files": sorted(os.listdir(published)),
    }
    with open(os.path.join(published, "run_manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
    print(f"Run manifest written to {published}/run_manifest.json")


def main():
    parser = argparse.ArgumentParser(description="DSS150P Fire Risk Reproducible Pipeline")
    parser.add_argument(
        "--step",
        choices=[
            "ingest", "validate", "transform", "build-curated",
            "storage", "train", "evaluate", "reproducibility-check",
            "publish", "all",
        ],
        required=True,
    )
    parser.add_argument("--force", action="store_true", help="Force full refresh")
    parser.add_argument("--stage", choices=["raw", "curated"], default="raw")
    parser.add_argument(
        "--run-id",
        default=f"local_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
    )
    args = parser.parse_args()

    print(f"Pipeline Run ID: {args.run_id}")

    if args.step in ["ingest", "all"]:
        print("\n" + "=" * 50); print("STEP 1: INGESTION"); print("=" * 50)
        ingest_data(
            "data/source/industrial_fire_risk_data.csv",
            "data/raw/",
            "metadata/checkpoint.json",
            force=args.force,
        )

    if args.step in ["validate", "all"] and args.stage == "raw":
        print("\n" + "=" * 50); print("VALIDATE: RAW"); print("=" * 50)
        from validate import validate_data
        batches = sorted(glob.glob("data/raw/batch_*.csv"))
        if not batches:
            raise FileNotFoundError("No raw batches found in data/raw/")
        for batch in batches:
            validate_data(batch, stage="raw")

    if args.step in ["transform", "all"]:
        print("\n" + "=" * 50); print("STEP 2: STAGING"); print("=" * 50)
        build_staging("data/raw/", "data/staging/")

    if args.step in ["build-curated", "all"]:
        print("\n" + "=" * 50); print("STEP 3: CURATED"); print("=" * 50)
        build_curated(
            "data/staging/staging.csv",
            "data/curated/cleaned_fire_risk_data.csv",
        )

    if args.step in ["validate", "all"] and args.stage == "curated":
        print("\n" + "=" * 50); print("VALIDATE: CURATED"); print("=" * 50)
        from validate import validate_data
        validate_data("data/curated/cleaned_fire_risk_data.csv", stage="curated")

    if args.step in ["storage", "all"]:
        print("\n" + "=" * 50); print("STEP 4: STORAGE BENCHMARK"); print("=" * 50)
        run_benchmark("data/curated/cleaned_fire_risk_data.csv")

    if args.step in ["train", "all"]:
        print("\n" + "=" * 50); print("STEP 5: MODEL TRAINING"); print("=" * 50)
        train_model(
            "data/curated/cleaned_fire_risk_data.csv",
            "outputs/model/",
            "outputs/metrics.json",
            "outputs/predictions.csv",
        )

    if args.step in ["evaluate", "all"]:
        print("\n" + "=" * 50); print("STEP 6: EVALUATION"); print("=" * 50)
        compare_metrics("outputs/metrics.json", "metadata/expected_metrics.json")

    if args.step in ["reproducibility-check", "all"]:
        print("\n" + "=" * 50); print("STEP 7: REPRODUCIBILITY CHECK"); print("=" * 50)
        step_reproducibility_check(args.run_id)

    if args.step in ["publish", "all"]:
        print("\n" + "=" * 50); print("STEP 8: PUBLISH"); print("=" * 50)
        _publish_outputs(args.run_id)


if __name__ == "__main__":
    main()