# Runbook: Fire Risk Reproducible Pipeline

## 0. Architecture at a glance

The project uses **two Docker Compose files** on a **shared external network**:

| File | Services | Purpose |
|---|---|---|
| `docker-compose.yml` | `db`, `pipeline` | Application PostgreSQL + standalone CLI runner |
| `docker-compose.airflow.yml` | `airflow-db`, `airflow-init`, `airflow-webserver`, `airflow-scheduler` | Airflow orchestration stack |

Both stacks attach to the external network `dss150p-net` so the DAG inside Airflow can reach the application database by service name (`db`).

Create the network once per machine:

    docker network create dss150p-net

---

## 1. Normal Execution

### Option A — Local (virtual environment)

Activate the venv, then run the full pipeline from scratch:

    python src/cli.py --step all --force

### Option B — Docker (reproducible, no local Python needed)

    docker network create dss150p-net     # once
    docker compose -f docker-compose.yml up -d --build
    docker compose run --rm pipeline

### Option C — Airflow-orchestrated (Phase IV demo)

    docker network create dss150p-net     # once
    docker compose -f docker-compose.yml up -d --build
    docker compose -f docker-compose.airflow.yml up --build

Wait for `airflow-init` to log `Migrations done` and `User "airflow" created`, then open
http://localhost:8080 (login `airflow` / `airflow`), unpause `predictive_repro_pipeline`,
and click **Trigger DAG**.

---

## 2. Common Failures & Resolutions

| Symptom | Cause | Fix |
|---|---|---|
| `FileNotFoundError: data/source/industrial_fire_risk_data.csv` | Source dataset not placed | Download from Kaggle (`joganimitesh/industrial-fire-and-accident-risk-predictor`) and place it in `data/source/` |
| `ModuleNotFoundError` | Deps missing in local venv | `pip install -r requirements.txt` |
| `psycopg2.OperationalError: could not translate host name "db"` | Airflow container cannot reach the app DB | Ensure both compose files declare `networks: { default: { name: dss150p-net, external: true } }` and run `docker network create dss150p-net` |
| `psycopg2.OperationalError: connection refused` (local run) | Postgres container not running | `docker compose -f docker-compose.yml up -d db` |
| `sqlalchemy.exc.OperationalError: unable to open database file` | Airflow init tried SQLite on a root-owned volume | Switch Airflow metadata DB to Postgres (already configured in `docker-compose.airflow.yml`) |
| `You need to initialize the database. Please run airflow db init` | `airflow-init` did not run or failed | `docker compose -f docker-compose.airflow.yml down --volumes` then `up --build`; watch `docker logs -f airflow-init` |
| `Airflow webserver keeps restarting` | Docker Desktop RAM too low | Settings → Resources → allocate ≥ 4 GB RAM |
| `healthcheck failed: curl: not found` | `curl` missing in Airflow image | Verify `Dockerfile.airflow` installs `curl` (see Dockerfile in repo) |
| `ImportError: libgomp.so.1` (XGBoost) | Missing system lib in app image | Verify `Dockerfile` installs `libgomp1` |
| `Pipeline skips batches` | Checkpointing working as designed | Use `--force` to reset and reprocess all batches |
| `Duplicate rows after rerun` | Loader is not idempotent | Check `sql/schema.sql` uses `ON CONFLICT` or `MERGE` on the business key |

PostgreSQL being unavailable is **not fatal** for local runs: the pipeline will still
emit CSV / JSON / Parquet benchmarks. Only the Postgres timings are skipped.

---

## 3. Restart / Rerun Procedures
Full pipeline from scratch `python src/cli.py --step all --force`

#### To run individual steps:
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


## 4. Checkpoint Recovery

The ingestion step splits the source CSV into **three deterministic batches** and
records progress in `metadata/checkpoint.json`.

| Situation | Action |
|---|---|
| Resume after an interrupted run | `python src/cli.py --step ingest` (skips committed batches) |
| Force a fresh full ingestion | `python src/cli.py --step ingest --force` |
| Manually reset the checkpoint | Delete `metadata/checkpoint.json` and rerun ingestion |

**Recovery demonstration (Phase IV evidence):**

1. Run `python src/cli.py --step ingest` — observe batch 1 completes, then stop with `Ctrl+C`.
2. Inspect `metadata/checkpoint.json` — batch 1 marked committed.
3. Rerun `python src/cli.py --step ingest` — batch 1 is skipped, batches 2 and 3 process.
4. Verify no duplicate raw rows: count of `data/raw/*.csv` equals original source rows.

---

## 5. Database Reset (PostgreSQL)

### Application DB (`docker-compose.yml`)

    docker compose -f docker-compose.yml down -v
    docker compose -f docker-compose.yml up -d db
    python src/storage.py
    # or, in Docker:
    docker compose -f docker-compose.yml run --rm pipeline \
        python src/cli.py --step storage --force

### Airflow metadata DB (`docker-compose.airflow.yml`)

This is separate from the application DB. Reset it only if the Airflow schema is
corrupted or you changed the Airflow version:

    docker compose -f docker-compose.airflow.yml down --volumes --remove-orphans
    docker compose -f docker-compose.airflow.yml up --build

`airflow-init` will re-run `airflow db migrate` and recreate the admin user.

---

## 6. Rollback / Cleanup

### Full project cleanup

**Windows PowerShell:**

    Remove-Item -Recurse -Force data/raw/*, data/staging/*, data/curated/*, data/quarantine/*, outputs/*, metadata/checkpoint.json
    docker compose -f docker-compose.airflow.yml down --volumes
    docker compose -f docker-compose.yml down -v

**Mac/Linux:**

    rm -rf data/raw/* data/staging/* data/curated/* data/quarantine/* outputs/* metadata/checkpoint.json
    docker compose -f docker-compose.airflow.yml down --volumes
    docker compose -f docker-compose.yml down -v

**Remove the shared network (only if no other project uses it):**

    docker network rm dss150p-net

### Partial cleanup

| Artifact | Command |
|---|---|
| Raw batches only | `rm -rf data/raw/* metadata/checkpoint.json` |
| Staging only | `rm -rf data/staging/*` |
| Curated only | `rm -rf data/curated/*` |
| Model + outputs only | `rm -rf outputs/*` |

After cleanup, re-run the full pipeline with `python src/cli.py --step all --force`.

---

## 7. Airflow Operations

### Start

    docker network create dss150p-net                                    # once
    docker compose -f docker-compose.yml up -d --build                   # app DB
    docker compose -f docker-compose.airflow.yml up --build              # Airflow

### Verify containers

    docker compose -f docker-compose.airflow.yml ps

Expected steady state:

    airflow-db             Up (healthy)
    airflow-init           Exited (0)
    airflow-webserver-1    Up (healthy)
    airflow-scheduler-1    Up

### Logs

    docker compose -f docker-compose.airflow.yml logs -f airflow-init
    docker compose -f docker-compose.airflow.yml logs -f airflow-webserver
    docker compose -f docker-compose.airflow.yml logs -f airflow-scheduler

### Manual DAG trigger (CLI alternative to the UI)

    docker exec -it dss150p_repro_toliba_gab-airflow-scheduler-1 \
      airflow dags trigger predictive_repro_pipeline \
      --conf '{"force": true}'

### Shut down

    docker compose -f docker-compose.airflow.yml down
    docker compose -f docker-compose.yml down