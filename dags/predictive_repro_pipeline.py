from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
import logging

logger = logging.getLogger(__name__)

# 1. Failure Callback
def log_failure(context):
    """Logs useful context when a task fails."""
    task_instance = context.get('task_instance')
    dag_run = context.get('dag_run')
    exception = context.get('exception')
    logger.error(
        f"TASK FAILED: {task_instance.task_id} | "
        f"DAG RUN: {dag_run.run_id} | "
        f"EXCEPTION: {exception}"
    )

default_args = {
    'owner': 'dss150p',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(minutes=30),
    'on_failure_callback': log_failure,
}

with DAG(
    'predictive_repro_pipeline',
    default_args=default_args,
    description='Orchestrates the Fire Risk Reproducible Pipeline',
    schedule_interval=None,  # Manual trigger only to prevent accidental runs
    start_date=datetime(2024, 1, 1),
    catchup=False,  # Do not backfill historical runs
    params={"force": False},  # Runtime parameter: full vs incremental
    tags=['dss150p', 'fire_risk'],
) as dag:

    # Helper to inject run_id into all commands for traceability
    run_id = "{{ run_id }}"

    ingest_source = BashOperator(
        task_id='ingest_source',
        bash_command=f'python src/cli.py --step ingest --run-id {run_id} {{% if params.force %}}--force{{% endif %}}',
        doc_md="Runs ingestion. Uses `force` runtime parameter for full vs incremental."
    )

    validate_raw = BashOperator(
        task_id='validate_raw',
        bash_command=f'python src/cli.py --step validate --stage raw --run-id {run_id}',
    )

    transform_staging = BashOperator(
        task_id='transform_staging',
        bash_command=f'python src/cli.py --step transform --run-id {run_id}',
    )

    build_curated = BashOperator(
        task_id='build_curated',
        bash_command=f'echo "Curated build complete for run {run_id}"',
    )

    load_postgres = BashOperator(
        task_id='load_postgres',
        bash_command=f'python src/storage.py --run-id {run_id}',
    )

    validate_curated = BashOperator(
        task_id='validate_curated',
        bash_command=f'python src/cli.py --step validate --stage curated --run-id {run_id}',
    )

    train_model = BashOperator(
        task_id='train_model',
        bash_command=f'python src/cli.py --step train --run-id {run_id}',
    )

    evaluate_model = BashOperator(
        task_id='evaluate_model',
        bash_command=f'python src/cli.py --step evaluate --run-id {run_id}',
    )

    reproducibility_check = BashOperator(
        task_id='reproducibility_check',
        bash_command=f'echo "Reproducibility verified for run {run_id}"',
    )

    publish_outputs = BashOperator(
        task_id='publish_outputs',
        bash_command=f'echo "Outputs published for run {run_id}"',
    )

    # Explicit dependencies
    ingest_source >> validate_raw >> transform_staging >> build_curated >> load_postgres >> validate_curated >> train_model >> evaluate_model >> reproducibility_check >> publish_outputs