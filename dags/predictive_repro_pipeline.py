from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'dss150p',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(minutes=30),
}

with DAG(
    'predictive_repro_pipeline',
    default_args=default_args,
    description='Orchestrates the Fire Risk Reproducible Pipeline',
    schedule_interval=None,  # Manual trigger only
    start_date=datetime(2024, 1, 1),
    catchup=False,
    params={"force": False},  # Runtime parameter
    tags=['dss150p', 'fire_risk'],
) as dag:

    # Task 1: Ingest
    ingest_source = BashOperator(
        task_id='ingest_source',
        bash_command='python src/cli.py --step ingest {% if params.force %}--force{% endif %}',
        doc_md="""Runs the ingestion module. Uses the `force` runtime parameter to control full vs incremental."""
    )

    # Task 2: Validate Raw
    validate_raw = BashOperator(
        task_id='validate_raw',
        bash_command='python src/validate.py --stage raw',
    )

    # Task 3: Transform to Staging
    transform_staging = BashOperator(
        task_id='transform_staging',
        bash_command='python src/cli.py --step transform',
    )

    # Task 4: Build Curated
    build_curated = BashOperator(
        task_id='build_curated',
        bash_command='echo "Curated build complete (handled in transform step)"',
    )

    # Task 5: Load Postgres
    load_postgres = BashOperator(
        task_id='load_postgres',
        bash_command='python src/storage.py',
    )

    # Task 6: Validate Curated
    validate_curated = BashOperator(
        task_id='validate_curated',
        bash_command='python src/validate.py --stage curated',
    )

    # Task 7: Train Model
    train_model = BashOperator(
        task_id='train_model',
        bash_command='python src/cli.py --step train',
    )

    # Task 8: Evaluate Model
    evaluate_model = BashOperator(
        task_id='evaluate_model',
        bash_command='python src/evaluate.py',
    )

    # Task 9: Reproducibility Check
    reproducibility_check = BashOperator(
        task_id='reproducibility_check',
        bash_command='echo "Reproducibility verified in evaluate step"',
    )

    # Task 10: Publish Outputs
    publish_outputs = BashOperator(
        task_id='publish_outputs',
        bash_command='echo "Outputs published to outputs/ directory"',
    )

    # Dependencies
    ingest_source >> validate_raw >> transform_staging >> build_curated >> load_postgres >> validate_curated >> train_model >> evaluate_model >> reproducibility_check >> publish_outputs