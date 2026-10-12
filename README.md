# Dynamic Industrial Fire Hazard Assessment Pipeline

## Purpose
This project converts a previously exploratory Jupyter Notebook analysis into a fully reproducible, modular data engineering pipeline. It uses IIoT telemetry from four factories to predict a continuous `Risk` score (0-100), supporting early fire hazard detection through thermal monitoring and preventive maintenance.

## Architecture
The pipeline follows a strict data flow:
1. **Ingestion:** Source CSV is split into 3 deterministic batches (with checkpoints).
2. **Transformation:** Raw batches are combined, cleaned, encoded, and enriched with interaction features.
3. **Storage Benchmark:** Curated data is materialized as CSV, JSON, Parquet, and PostgreSQL.
4. **Modeling:** A Random Forest Regressor is trained on an 80/20 chronological split.
5. **Evaluation:** Actual metrics are automatically compared against the expected baseline.
6. **Orchestration:** Apache Airflow DAG (`dags/predictive_repro_pipeline.py`) coordinates all steps.

### Documentation Artifacts
- `docs/architecture.txt`: Software component diagram.
- `docs/lineage.txt`: Data artifact and transformation flow. *(Note: Created as .txt instead of .png due to local environment constraints).*
- `docs/runbook.md`: Operational instructions and recovery procedures.
- `docs/reproducibility_report.md`: Baseline vs. engineered reproduction comparison.

## Prerequisites
- Python 3.10+
- Git
- Docker (for PostgreSQL and Airflow)
- pip (Python package manager)

## Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/Gabbygabo/dss-lab4.git
   cd DSS150P_REPRO_TOLIBA_GAB

## Create and activate virtual environment:
```
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

## Install dependencies
`pip install -r requirements.txt`

## Create own environment file:
`cp .env.example .env`

## Data Placement / Acquisition
1. Download the dataset from kaggle: https://www.kaggle.com/datasets/joganimitesh/industrial-fire-and-accident-risk-predictor
2. Place it here: data/source/industrial_fire_risk_data.csv

## Execution commands:
To run the entire pipeline (Ingestion -> Transformation -> Storage -> Training) from scratch:
`python src/cli.py --step all --force`

To run individual steps:
```
Ingestion only: python src/cli.py --step ingest
Transformation only: python src/cli.py --step transform
Storage Benchmark only: python src/cli.py --step storage
Training only: python src/cli.py --step train
```

## Airflow instructions
To start the Airflow webserver and scheduler via Docker:
`docker compose -f docker-compose.airflow.yml up -d --build`

THEN:
1. Open your browser to http://localhost:8080.
2. Login with: airflow / airflow.
3. Toggle on the predictive_repro_pipeline DAG.
4. Click "Trigger DAG" to run. You can pass {"force": true} in the config JSON to simulate a full refresh.
5. To shut down: docker compose -f docker-compose.airflow.yml down

## Validation
To run the data quality assertions and integration tests:
`python -m pytest tests/test_pipeline.py -v`

To verify reproducibility against the baseline: 
`python src/evaluate.py`

## Expected Outputs
After a successful run, the following files will be created:
* data/curated/cleaned_fire_risk_data.csv (98,000 rows, 26 features)
* outputs/metrics.json (Expected: MSE 10.47, RMSE 3.24, MAE 2.57, R² 0.96)
* outputs/predictions.csv (Actual vs Predicted)
* outputs/model/random_forest_model.pkl
* docs/benchmark_report.md (CSV vs JSON vs Parquet vs PostgreSQL timings)

## Troubleshooting
* ModuleNotFoundError: Run pip install -r requirements.txt.
* FileNotFoundError: data/source/industrial_fire_risk_data.csv: Download the Kaggle dataset and place it in data/source/.
* PostgreSQL connection refused: Ensure Docker Desktop is running and execute docker compose up -d db.
* Airflow webserver keeps restarting: Increase Docker Desktop memory limit to at least 4GB in Settings -> Resources.
* Pipeline skips batches: This is expected behavior due to checkpointing. Run with --force to reset and process all batches.


## Engineering-Gap Analysis

| Current Behavior (Old Project) | Risk | DSS150P Concept | Remediation |
| :--- | :--- | :--- | :--- |
| Dataset loaded from personal desktop path | Cannot run elsewhere | Relative/configured paths; dataset manifest | Moved dataset to `data/source/`, implemented `src/cli.py` with relative paths. |
| Random train/test split without seed | Metrics change every run | Fixed seed and split manifest | Hardcoded `random_state=42` and chronological 80/20 split in `src/train.py`. |
| Notebook cells run out of order | Hidden execution state | Modular functions + command entry point | Converted notebooks to `src/ingest.py`, `src/transform.py`, `src/train.py`, and unified them in `src/cli.py`. |
| Manual data cleaning | Not repeatable | Staging transformation code | Automated cleaning in `src/transform.py` (dropna, datetime parsing, encoding, interactions). |
| Model metric only visible in notebook | No machine-readable output | Persist metrics.json + comparison check | `src/train.py` saves `outputs/metrics.json` and `outputs/predictions.csv`. |
| No source verification | Data drift/silent corruption | SHA-256 checksum in manifest | Generated checksum and stored in `metadata/source_manifest.yml`. |

### note for architecture.png and lineage.png
Due to time-constraints and that I am not feeling well while doing the activity, I used .txt instead.