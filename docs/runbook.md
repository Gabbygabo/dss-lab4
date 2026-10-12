# Runbook: Fire Risk Reproducible Pipeline

## 1. Normal Execution
To run the entire pipeline from scratch (recommended for a clean environment):
```
python src/cli.py --step all --force
```

## 2. Common Failures & Resolutions
* Missing Source Data: If data/source/industrial_fire_risk_data.csv is missing, the pipeline will fail immediately. Download it from Kaggle (joganimitesh/industrial-fire-and-accident-risk-predictor) and place it in that folder.
* PostgreSQL Skipped / Connection Refused: This is not a fatal error. The pipeline will still generate CSV, JSON, and Parquet benchmarks. To get PostgreSQL metrics, ensure Docker Desktop is running and execute docker compose up -d db.
* Airflow Webserver Looping: If the Airflow container keeps restarting, it means it ran out of memory. Go to Docker Desktop -> Settings -> Resources and allocate at least 4GB of RAM.
* ModuleNotFoundError: Run pip install -r requirements.txt to ensure all dependencies are installed.
* FileNotFoundError (data/source): You forgot to download the Kaggle dataset. See the "Missing Source Data" section above.

## 3. Restart/rerun procedures
To run the entire pipeline (Ingestion -> Transformation -> Storage -> Training) from scratch:
```
python src/cli.py --step all --force
```
To run individual steps:
* Ingestion only: 
```
python src/cli.py --step ingest
```
* Transformation only: 
```
python src/cli.py --step transform
```
* Storage Benchmark only: 
```
python src/cli.py --step storage
```
* Training only: 
```
python src/cli.py --step train
```

## 4. Checkpoint recovery
* The ingestion process uses a checkpoint file (metadata/checkpoint.json) to track which batches have been committed.
* To resume from where you left off: Simply run python src/cli.py --step ingest. It will skip already committed batches.
* To simulate a fresh start (recovery test): Run python src/cli.py --step ingest --force. This ignores the checkpoint and re-processes all batches.
* To manually reset the checkpoint: Delete metadata/checkpoint.json and run the ingestion again.

## 5. Database Reset (PostgreSQL)
If your PostgreSQL database becomes corrupted or you want to wipe all data and start fresh:
```
docker compose down -v
docker compose up -d db
python src/storage.py
```

## 6. Rollback / Cleanup
To completely reset the pipeline and remove all generated artifacts (data, models, and outputs), run:

 On Windows PowerShell:
```
Remove-Item -Recurse -Force data/raw/*, data/curated/*, outputs/*, metadata/checkpoint.json
```
 On Mac/Linux:
```
rm -rf data/raw/* data/curated/* outputs/* metadata/checkpoint.json
```

After cleanup, you can re-run the full pipeline with python src/cli.py --step all --force

## 7. Airflow Operations
To start Airflow:
```
docker compose -f docker-compose.airflow.yml up -d --build
```

To view logs for the scheduler (useful for debugging DAG failures):
```
docker compose -f docker-compose.airflow.yml logs -f airflow-scheduler
```

To shut down Airflow:
```
docker compose -f docker-compose.airflow.yml down
```