# Reproducibility Report

## 1. Prior Project Baseline
- **Model Family:** Random Forest Regressor
- **Target:** Risk (continuous)
- **Train/Test Strategy:** Chronological 80/20 split
- **Random Seed:** 42
- **Reported Metrics:** RMSE: 3.24, MAE: 2.57, R²: 0.96

## 2. Engineered Reproduction
- **Model Family:** Random Forest Regressor
- **Target:** Risk (continuous)
- **Train/Test Strategy:** Chronological 80/20 split (boundary index: 78400)
- **Random Seed:** 42
- **Actual Metrics:** RMSE: 3.24, MAE: 2.57, R²: 0.96

## 3. Metric Consistency
The actual metrics perfectly match the expected baseline with a difference of 0.0000, well within the 0.01 tolerance.

## 4. Deterministic Controls
- All `random_state` parameters set to 42.
- Chronological split ensures no data leakage from future timestamps.
- Preprocessing is deterministic and fitted only on the training set.

## 5. Known Limitations
- The `Risk` score may be a synthetically derived composite. The model is reconstructing a formula rather than discovering a physical law. Validation on an independent dataset is recommended.



-----------------------------
## PHASE IV: REPRODUCIBILITY
#### 0. this was done on the cloned repo

C:\Users\Lenovo Thinkpad T460>git clone https://github.com/Gabbygabo/dss-lab4.git
Cloning into 'dss-lab4'...
remote: Enumerating objects: 174, done.
remote: Counting objects: 100% (174/174), done.
remote: Compressing objects: 100% (116/116), done.
remote: Total 174 (delta 72), reused 150 (delta 51), pack-reused 0 (from 0)
Receiving objects: 100% (174/174), 185.09 KiB | 2.61 MiB/s, done.
Resolving deltas: 100% (72/72), done.

### 1. Show the GitHub repository and commit history.

C:\Users\Lenovo Thinkpad T460\dss-lab4>git log --oneline -n 15
f32d2f8 (HEAD -> main, origin/main, origin/HEAD) docs: updated runbook.md and README.md
7960e0d test: capture PostgreSQL evidence and reproducibility report
6cc8d31 feat: orchestrate pipeline with Airflow; stage-guard validation
e674a81 feat: split staging and curated layers; rerun-safe PostgreSQL load
ec5ecb9 chore: pin dependencies, configure Docker environment and ignore rules
2debaef 07 feat: update Airflow DAG with traceability, failure logging, and evidence
6641372 polished runbook.md
5422e5d polished runbook.md
bfcb918 polished runbook.md
68c7d1f polishing README.md
90b9c1f polishing README.md
90f1ab8 updated README.md
52e95bf 10 docs: updated README and runbook documentation
57d123f updated README.md
72a3478 Updated README.md

### 2. Show that `.env`/secrets and generated large artifacts are not improperly committed

C:\Users\Lenovo Thinkpad T460\dss-lab4>dir /a
 Volume in drive C has no label.
 Volume Serial Number is E057-76AE

 Directory of C:\Users\Lenovo Thinkpad T460\dss-lab4

13/10/2026  12:59 pm    <DIR>          .
13/10/2026  12:59 pm    <DIR>          ..
13/10/2026  12:59 pm               324 .dockerignore
13/10/2026  12:59 pm                80 .env.example
13/10/2026  12:59 pm    <DIR>          .git
13/10/2026  12:59 pm             1,149 .gitignore
13/10/2026  12:59 pm    <DIR>          config
13/10/2026  12:59 pm    <DIR>          dags
13/10/2026  12:59 pm             2,281 docker-compose.airflow.yml
13/10/2026  12:59 pm               750 docker-compose.yml
13/10/2026  12:59 pm               303 Dockerfile
13/10/2026  12:59 pm               979 Dockerfile.airflow
13/10/2026  12:59 pm    <DIR>          docs
13/10/2026  12:59 pm    <DIR>          metadata
13/10/2026  12:59 pm    <DIR>          outputs
13/10/2026  12:59 pm             7,524 README.md
13/10/2026  12:59 pm               195 requirements.txt
13/10/2026  12:59 pm    <DIR>          sql
13/10/2026  12:59 pm    <DIR>          src
13/10/2026  12:59 pm    <DIR>          tests
               9 File(s)         13,585 bytes
              11 Dir(s)  47,634,956,288 bytes free
    
### 3. Verify source dataset checksum against `source_manifest.yml`.

C:\Users\Lenovo Thinkpad T460\dss-lab4>certutil -hashfile data\source\industrial_fire_risk_data.csv SHA256
SHA256 hash of data\source\industrial_fire_risk_data.csv:
6457d041b0215399f867ee0855aa136f859ff541714ebb8fed56cb4a43b44536
CertUtil: -hashfile command completed successfully.

### 4. Build/start the environment using documented commands.

C:\Users\Lenovo Thinkpad T460\dss-lab4>docker compose -f docker-compose.yml up -d --build

...
[+] up 3/3
 ✔ Image dss-lab4-pipeline       Built                                                                                                                                 13.3s ✔ Container dss-lab4-db-1       Healthy                                                                                                                               16.7s ✔ Container dss-lab4-pipeline-1 Started                                                                                                                                0.9s
 
 C:\Users\Lenovo Thinkpad T460\dss-lab4>docker compose -f docker-compose.airflow.yml up -d --build
 
 [+] up 3/3
 ✔ Image dss-lab4-airflow-init      Built                                         492.2s ✔ Image dss-lab4-airflow-webserver Built                                         492.2s ✔ Image dss-lab4-airflow-scheduler Built                                         492.2stime="2026-10-13T13:42:10+08:00" level=warning msg="Found orphan containers (dss-lab4-pipeline-1, dss-lab4-db-1) for this project. If you removed or renamed this service in your compose file, you can run this command with the --remove-orphans flag to clean it up."[+] up 8/8-10-13T13:42:10+08:00" level=warning msg="network \"dss-lab4_default\" (id 942 ✔ Image dss-lab4-airflow-init            Built                                   492.2s ✔ Image dss-lab4-airflow-webserver       Built                                   492.2s ✔ Image dss-lab4-airflow-scheduler       Built                                   492.2s ✔ Volume dss-lab4_airflow-db-volume      Created                                   0.1s ✔ Container dss-lab4-airflow-db-1        Healthy                                  20.7s ✔ Container dss-lab4-airflow-init-1      Exited                                   45.2s ✔ Container dss-lab4-airflow-scheduler-1 Started                                  45.6s ✔ Container dss-lab4-airflow-webserver-1 Started                                  45.9s
 
 ### 5. Execute the end-to-end pipeline manually or through Airflow as instructed in the README
 * note: since my laptop lacks physical RAM left to support Windows, Docker, PostgreSQL, and the Airflow webserver all at the same time. Airflow is just too heavy for my local hardware. I manually executed the pipeline.
 
 [+]  1/1t 1/11o Thinkpad T460\dss-lab4>docker compose -f docker-compose.yml run --rm pipeline python src/cli.py --step all --force
 ✔ Container dss-lab4-db-1 Started                                                                                                                                      3.0sContainer dss-lab4-db-1 Waiting f you removed or renamed this service in your compose file, you can run this command with the --remove-orphans flag to clean it up."
Container dss-lab4-db-1 Healthy
Container dss-lab4-pipeline-run-76713215e7bb Creating
Container dss-lab4-pipeline-run-76713215e7bb Created
Pipeline Run ID: local_20261013_060412

==================================================
STEP 1: INGESTION
==================================================
Starting ingestion from data/source/industrial_fire_risk_data.csv...
Processing batch 1...
Batch 1 committed. Checkpoint advanced.
Processing batch 2...
Batch 2 committed. Checkpoint advanced.
Processing batch 3...
Batch 3 committed. Checkpoint advanced.
Ingestion complete.

==================================================
VALIDATE: RAW
==================================================
Running Data Quality Checks on raw data: data/raw/batch_1.csv
VALIDATION PASSED: All data quality checks passed.
Running Data Quality Checks on raw data: data/raw/batch_2.csv
VALIDATION PASSED: All data quality checks passed.
Running Data Quality Checks on raw data: data/raw/batch_3.csv
VALIDATION PASSED: All data quality checks passed.

==================================================
STEP 2: STAGING
==================================================
Building staging from data/raw/...
Combined 3 batches into 100000 rows.
Quarantined 2000 rows -> data/quarantine/rejected_records.csv
Staging written: data/staging/staging.csv (98000 rows, 26 cols)

==================================================
STEP 3: CURATED
==================================================
Building curated from data/staging/staging.csv...
Loaded 98000 staging rows.
Curated written: data/curated/cleaned_fire_risk_data.csv (98000 rows, 27 cols)

==================================================
STEP 4: STORAGE BENCHMARK
==================================================
Loading curated data for storage benchmark...
Benchmarking CSV...
Benchmarking JSON...
Benchmarking Parquet...
Benchmarking PostgreSQL...
  -> Wrote 98000 rows to fire_risk
Demonstrating Partitioning...
  -> Loaded 1 partition with 1000 rows.
Benchmark complete. Report saved to docs/benchmark_report.md

==================================================
STEP 5: MODEL TRAINING
==================================================
Loading data from data/curated/cleaned_fire_risk_data.csv...
Split manifest saved to metadata/split_manifest.json
Training Random Forest on 78400 samples...

--- Model Performance ---
MSE: 10.47
RMSE: 3.24
MAE: 2.57
R2: 0.96
Metrics saved to outputs/metrics.json
Predictions saved to outputs/predictions.csv
Model saved to outputs/model/random_forest_model.pkl

==================================================
STEP 6: EVALUATION
==================================================
Evaluating reproducibility...
Expected RMSE: 3.24
Actual RMSE:   3.24
Difference:          0.0000 (Tolerance: 0.01)

REPRODUCIBILITY PASSED: Metrics match within tolerance.

==================================================
STEP 7: REPRODUCIBILITY CHECK
==================================================
Reproducibility report written to outputs/reproducibility_report.json
Overall pass: True

==================================================
STEP 8: PUBLISH
==================================================
Copied outputs/metrics.json -> outputs/published/metrics.json
Copied outputs/predictions.csv -> outputs/published/predictions.csv
Copied outputs/reproducibility_report.json -> outputs/published/reproducibility_report.json
Run manifest written to outputs/published/run_manifest.json
 
### 6. Show raw, staging, curated, and final predictive outputs.

C:\Users\Lenovo Thinkpad T460\dss-lab4>dir data\curated
 Volume in drive C has no label.
 Volume Serial Number is E057-76AE

 Directory of C:\Users\Lenovo Thinkpad T460\dss-lab4\data\curated

13/10/2026  01:33 pm    <DIR>          .
13/10/2026  01:33 pm    <DIR>          ..
13/10/2026  02:04 pm        10,895,857 cleaned_fire_risk_data.csv
               1 File(s)     10,895,857 bytes
               2 Dir(s)  37,909,123,072 bytes free

C:\Users\Lenovo Thinkpad T460\dss-lab4>dir outputs
 Volume in drive C has no label.
 Volume Serial Number is E057-76AE

 Directory of C:\Users\Lenovo Thinkpad T460\dss-lab4\outputs

13/10/2026  01:40 pm    <DIR>          .
13/10/2026  01:40 pm    <DIR>          ..
13/10/2026  01:34 pm    <DIR>          benchmark
13/10/2026  02:10 pm                71 metrics.json
13/10/2026  01:39 pm    <DIR>          model
13/10/2026  12:59 pm                 0 prediction.csv
13/10/2026  02:10 pm           435,959 predictions.csv
13/10/2026  01:40 pm    <DIR>          published
13/10/2026  02:10 pm               750 reproducibility_report.json
               4 File(s)        436,780 bytes
               5 Dir(s)  37,909,000,192 bytes free

### 7. Show PostgreSQL target tables and relevant audit/run records.

C:\Users\Lenovo Thinkpad T460\dss-lab4>docker exec -it dss-lab4-db-1 psql -U admin -d firerisk -c "SELECT * FROM fire_risk LIMIT 5;"
 Workers | Temp  | Pressure | Humidity | Vibration |  Speed  | Age | Service_Days | Gas  | Sparks | Risk  | Hour_of_Day | Day_of_Week | Is_Weekend | Month | Training_Encoded | Alarm_Encoded | Exp_Encoded | Factory_Factory_B | Factory_Factory_C | Factory_Factory_D | Region_Rural | Region_Urban | Shift_Night | Workers_Sparks_Interaction | Temp_Pressure_Interaction | Vibration_Speed_Interaction
---------+-------+----------+----------+-----------+---------+-----+--------------+------+--------+-------+-------------+-------------+------------+-------+------------------+---------------+-------------+-------------------+-------------------+-------------------+--------------+--------------+-------------+----------------------------+---------------------------+-----------------------------
       7 | 26.49 |    25.31 |    54.18 |      1.63 | 1007.06 |  17 |          202 |  8.9 |      1 | 56.47 |           0 |           4 |          0 |     1 |                1 |             0 |           0 |                 0 |                 0 |                 0 |            0 |            1 |           0 |                          7 |         670.4618999999999 |                   1641.5078
      11 | 24.59 |    19.98 |    68.53 |       3.1 | 2664.56 |   7 |          217 | 9.97 |      3 | 48.28 |           0 |           4 |          0 |     1 |                1 |             0 |           0 |                 0 |                 0 |                 0 |            0 |            0 |           1 |                         33 |                  491.3082 |                    8260.136
      14 | 26.94 |    24.62 |    79.44 |      4.31 | 2335.27 |   6 |           32 | 8.66 |      4 | 32.13 |           0 |           4 |          0 |     1 |                0 |             1 |           0 |                 0 |                 1 |                 0 |            0 |            1 |           0 |                         56 |         663.2628000000001 |                  10065.0137
      20 | 29.57 |    23.55 |    77.35 |      1.48 | 3806.65 |  10 |          276 | 2.71 |      1 | 59.04 |           0 |           4 |          0 |     1 |                0 |             0 |           1 |                 1 |                 0 |                 0 |            1 |            0 |           1 |                         20 |                  696.3735 |                    5633.842
      38 |  24.3 |    21.49 |    47.83 |      0.51 | 1147.47 |  16 |          303 | 5.87 |      4 | 53.32 |           1 |           4 |          0 |     1 |                0 |             1 |           0 |                 1 |                 0 |                 0 |            0 |            1 |           0 |                        152 |                   522.207 |                    585.2097
(5 rows)

### 8. Run data-quality and code tests.

C:\Users\Lenovo Thinkpad T460\dss-lab4>docker compose -f docker-compose.yml run --rm -v ./tests:/app/tests pipeline python -m pytest tests/ -v
time="2026-10-13T14:23:50+08:00" level=warning msg="Found orphan containers (dss-lab4-airflow-scheduler-1, dss-lab4-airflow-webserver-1, dss-lab4-airflow-init-1, dss-lab4-airflow-db-1) for this project. If you removed or renamed this service in your compose file, you can run this command with the --remove-orphans flag to clean it up."
[+]  1/1t 1/11
 ✔ Container dss-lab4-db-1 Running                                                  0.0sContainer dss-lab4-db-1 Waiting
Container dss-lab4-db-1 Healthy
Container dss-lab4-pipeline-run-222cd7ee255d Creating
Container dss-lab4-pipeline-run-222cd7ee255d Created
================================= test session starts ==================================platform linux -- Python 3.11.17, pytest-9.1.1, pluggy-1.6.0 -- /usr/local/bin/python
cachedir: .pytest_cache
rootdir: /app
collected 5 items

tests/test_pipeline.py::test_checksum_generation PASSED                                                                                                              [ 20%]
tests/test_pipeline.py::test_validate_data_passes PASSED                                                                                                             [ 40%]
tests/test_pipeline.py::test_validate_data_fails_on_missing_column PASSED                                                                                            [ 60%]
tests/test_pipeline.py::test_ingest_to_transform_integration PASSED                                                                                                  [ 80%]
tests/test_pipeline.py::test_train_to_output_integration PASSED                                                                                                      [100%]

============================================================================ 5 passed in 8.46s =============================================================================


### 9. Show Airflow dependency graph and completed run states.
* Due to local hardware memory constraints (OOM crash loops) preventing the Airflow webserver from stabilizing, the pipeline was executed manually via the containerized CLI, as permitted by the Phase IV Step 5 instructions.

### 10. Run the pipeline a second time and prove no duplicate logical records are introduced.

C:\Users\Lenovo Thinkpad T460\dss-lab4>docker exec -it dss-lab4-db-1 psql -U admin -d firerisk -c "SELECT COUNT(*) FROM fire_risk;"
 count
-------
 98000
(1 row)


What's next:
    Try Docker Debug for seamless, persistent debugging tools in any container or image → docker debug dss-lab4-db-1
    Learn more at https://docs.docker.com/go/debug-cli/

C:\Users\Lenovo Thinkpad T460\dss-lab4>docker compose -f docker-compose.yml run --rm pipeline python src/cli.py --step storage --run-id check_duplicates
time="2026-10-13T14:26:46+08:00" level=warning msg="Found orphan containers (dss-lab4-airflow-scheduler-1, dss-lab4-airflow-webserver-1, dss-lab4-airflow-init-1, dss-lab4-airflow-db-1) for this project. If you removed or renamed this service in your compose file, you can run this command with the --remove-orphans flag to clean it up."
[+]  1/1t 1/11
 ✔ Container dss-lab4-db-1 Running                                                                                                                                      0.0s
Container dss-lab4-db-1 Waiting
Container dss-lab4-db-1 Healthy
Container dss-lab4-pipeline-run-ad9757372a0e Creating
Container dss-lab4-pipeline-run-ad9757372a0e Created
Pipeline Run ID: check_duplicates

==================================================
STEP 4: STORAGE BENCHMARK
==================================================
Loading curated data for storage benchmark...
Benchmarking CSV...
Benchmarking JSON...
Benchmarking Parquet...
Benchmarking PostgreSQL...
  -> Wrote 98000 rows to fire_risk
Demonstrating Partitioning...
  -> Loaded 1 partition with 1000 rows.
Benchmark complete. Report saved to docs/benchmark_report.md

C:\Users\Lenovo Thinkpad T460\dss-lab4>docker exec -it dss-lab4-db-1 psql -U admin -d firerisk -c "SELECT COUNT(*) FROM fire_risk;"
 count
-------
 98000
(1 row)

### 11. Show baseline expected metrics and newly generated metrics side by side.

C:\Users\Lenovo Thinkpad T460\dss-lab4>type outputs\reproducibility_report.json
{
  "run_id": "local_20261013_060412",
  "tolerance": 0.01,
  "expected": {
    "baseline_model_family": "Random Forest Regressor",
    "target_variable": "Risk",
    "feature_set": "26 features (after one-hot encoding and interaction terms)",
    "train_test_strategy": "Chronological 80/20 split",
    "random_seed": 42,
    "preprocessing": "Drop missing Workers, Temporal extraction, Categorical encoding, Interaction terms",
    "hyperparameters": {
      "n_estimators": 100,
      "random_state": 42
    },
    "reported_metrics": {
      "MSE": 10.47,
      "RMSE": 3.24,
      "MAE": 2.57,
      "R2": 0.96
    }
  },
  "actual": {
    "MSE": 10.47,
    "RMSE": 3.24,
    "MAE": 2.57,
    "R2": 0.96
  },
  "per_metric": {},
  "pass": true
}

### 12. Demonstrate one failure/recovery scenario or show previously captured evidence with clear explanation.

C:\Users\Lenovo Thinkpad T460\dss-lab4>docker compose -f docker-compose.yml run --rm -v ./tests:/app/tests pipeline python -m pytest tests/ -v
time="2026-10-13T14:23:50+08:00" level=warning msg="Found orphan containers (dss-lab4-airflow-scheduler-1, dss-lab4-airflow-webserver-1, dss-lab4-airflow-init-1, dss-lab4-airflow-db-1) for this project. If you removed or renamed this service in your compose file, you can run this command with the --remove-orphans flag to clean it up."
[+]  1/1t 1/11
 ✔ Container dss-lab4-db-1 Running                                                  0.0sContainer dss-lab4-db-1 Waiting
Container dss-lab4-db-1 Healthy
Container dss-lab4-pipeline-run-222cd7ee255d Creating
Container dss-lab4-pipeline-run-222cd7ee255d Created
================================= test session starts ==================================platform linux -- Python 3.11.17, pytest-9.1.1, pluggy-1.6.0 -- /usr/local/bin/python
cachedir: .pytest_cache
rootdir: /app
collected 5 items

tests/test_pipeline.py::test_checksum_generation PASSED                                                                                                              [ 20%]
tests/test_pipeline.py::test_validate_data_passes PASSED                                                                                                             [ 40%]
tests/test_pipeline.py::test_validate_data_fails_on_missing_column PASSED                                                                                            [ 60%]
tests/test_pipeline.py::test_ingest_to_transform_integration PASSED                                                                                                  [ 80%]
tests/test_pipeline.py::test_train_to_output_integration PASSED                                                                                                      [100%]

============================================================================ 5 passed in 8.46s =============================================================================

#### To prevent bad data from silently reaching the machine learning model, this pipeline implements strict Data Contracts during the validation phase. As shown in the automated test results, the system was subjected to a deliberate failure injection via the test_validate_data_fails_on_missing_column test. When a required feature column is intentionally removed from the staging data:

* The Failure: The data contract validation immediately catches the schema violation and safely halts the pipeline execution, throwing an explicit error.

* The Recovery: The pipeline does not write corrupted or incomplete records to the PostgreSQL database (fire_risk table). Because the load process is idempotent and rerun-safe, an engineer can simply correct the source file schema and rerun the pipeline to resume normal operations without any duplicate or malformed data affecting the model's predictive integrity.

### 13. Explain one design decision you would change if the project became a real production system.
Currently, the entire pipeline—including the PostgreSQL database, the Airflow Webserver, the Scheduler, and the actual pipeline execution container—is tightly coupled and deployed on a single machine via docker-compose. As demonstrated during my local testing, Airflow is heavily resource-intensive. Running the orchestration layer on the same hardware as the data processing layer led to severe Out-Of-Memory (OOM) crash loops.

If this pipeline were moved to a real production environment with 100x the data volume, a single-node architecture would fail entirely. I would change the deployment strategy by decoupling the infrastructure into managed cloud services. I would migrate the PostgreSQL database to a managed instance like Amazon RDS to ensure high availability. For orchestration, instead of hosting Airflow directly, I would use a managed service like Cloud Composer (GCP) or MWAA (AWS). Finally, the actual data transformations and model training would execute on an auto-scaling Kubernetes cluster (EKS/GKE), ensuring the Airflow webserver never crashes due to heavy data processing workloads.