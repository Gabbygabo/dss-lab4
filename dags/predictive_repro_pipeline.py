from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
import logging

logger = logging.getLogger(__name__)

PROJECT_ROOT = "/opt/airflow"


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
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    params={"force": False},
    tags=['dss150p', 'fire_risk'],
) as dag:

    def cli_task(task_id, command, doc_md=None):
        return BashOperator(
            task_id=task_id,
            bash_command=command,
            cwd=PROJECT_ROOT,
            env={"PROJECT_ROOT": PROJECT_ROOT},
            doc_md=doc_md,
        )

    ingest_source = cli_task(
        "ingest_source",
        'python -u src/cli.py --step ingest --run-id "{{ run_id }}" '
        '{% if params.force %}--force{% endif %}',
        doc_md="Runs ingestion. Uses `force` runtime parameter for full vs incremental.",
    )

    validate_raw = cli_task(
        "validate_raw",
        'python -u src/cli.py --step validate --stage raw --run-id "{{ run_id }}"',
    )

    transform_staging = cli_task(
        "transform_staging",
        'python -u src/cli.py --step transform --run-id "{{ run_id }}"',
    )

    build_curated = cli_task(
        "build_curated",
        'python -u src/cli.py --step build-curated --run-id "{{ run_id }}"',
    )

    load_postgres = BashOperator(
        task_id="load_postgres",
        bash_command='python -u src/storage.py --run-id "{{ run_id }}"',
        cwd=PROJECT_ROOT,
        env={"PROJECT_ROOT": PROJECT_ROOT},
    )

    validate_curated = cli_task(
        "validate_curated",
        'python -u src/cli.py --step validate --stage curated --run-id "{{ run_id }}"',
    )

    train_model = cli_task(
        "train_model",
        'python -u src/cli.py --step train --run-id "{{ run_id }}"',
    )

    evaluate_model = cli_task(
        "evaluate_model",
        'python -u src/cli.py --step evaluate --run-id "{{ run_id }}"',
    )

    reproducibility_check = cli_task(
        "reproducibility_check",
        'python -u src/cli.py --step reproducibility-check --run-id "{{ run_id }}"',
        doc_md=(
            "Compares outputs/metrics.json against metadata/expected_metrics.json "
            "and writes outputs/reproducibility_report.json."
        ),
    )

    publish_outputs = cli_task(
        "publish_outputs",
        'python -u src/cli.py --step publish --run-id "{{ run_id }}"',
    )

    (
        ingest_source
        >> validate_raw
        >> transform_staging
        >> build_curated
        >> load_postgres
        >> validate_curated
        >> train_model
        >> evaluate_model
        >> reproducibility_check
        >> publish_outputs
    )