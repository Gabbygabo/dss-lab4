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
```
python src/cli.py --step all --force
```
To run individual steps:
```
python src/cli.py --step ingest        # raw batches
python src/cli.py --step validate      # raw validation
python src/cli.py --step transform     # raw → staging
python src/cli.py --step build-curated # staging → curated
python src/cli.py --step storage       # benchmark + Postgres load
python src/cli.py --step train         # model + metrics
python src/cli.py --step evaluate      # compare to baseline
python src/cli.py --step reproducibility-check
python src/cli.py --step publish
```

## Docker (no local Python required)
```
docker compose -f docker-compose.yml run --rm pipeline
```

## Airflow instructions

The project uses two Docker Compose files:
- `docker-compose.yml` — application PostgreSQL (`db`) and standalone pipeline runner
- `docker-compose.airflow.yml` — Airflow webserver, scheduler, and Airflow metadata DB

Both stacks must share a Docker network so the DAG can reach the application DB.

### 1. Create the shared network (once)

    docker network create dss150p-net

### 2. Start the application database

    docker compose -f docker-compose.yml up -d --build

### 3. Start the Airflow stack

    docker compose -f docker-compose.airflow.yml down --volumes --remove-orphans
    docker compose -f docker-compose.airflow.yml up --build

Wait for `airflow-init` to log `Migrations done` and `User "airflow" created`, then:

### 4. Open the UI

1. Browse to http://localhost:8080
2. Log in with `airflow` / `airflow`
3. Unpause the `predictive_repro_pipeline` DAG
4. Click **Trigger DAG** → pass `{"force": true}` in the config JSON for a full refresh
5. Monitor the **Graph View** for task states

### 5. Shut down

    docker compose -f docker-compose.airflow.yml down
    docker compose -f docker-compose.yml down

## Validation
#### source checksum verification
```
python -c "import hashlib, yaml; m = yaml.safe_load(open('metadata/source_manifest.yml')); h = hashlib.sha256(open('data/source/industrial_fire_risk_data.csv','rb').read()).hexdigest(); print('MATCH' if h == m['sha256_checksum'] else 'MISMATCH')"
```

## Data-quality and code tests
```
python -m pytest tests/ -v
```

## Verify reproducibility against the baseline: 
```
python src/evaluate.py
```

## Rerun-safety check (no duplicate logical records)
```
# run storage twice, count rows in between
docker compose -f docker-compose.yml run --rm pipeline python src/cli.py --step storage --run-id check1
docker exec -it dss150p_repro_toliba_gab-db-1 psql -U admin -d firerisk -c "SELECT COUNT(*) FROM fire_risk;"
docker compose -f docker-compose.yml run --rm pipeline python src/cli.py --step storage --run-id check2
docker exec -it dss150p_repro_toliba_gab-db-1 psql -U admin -d firerisk -c "SELECT COUNT(*) FROM fire_risk;"
```

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