from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import subprocess
import os

BASE_DIR = "/opt/airflow/project"
PYTHON   = "python3"

default_args = {
    "owner": "hexa",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}


def run_script(script_name: str) -> None:
    script_path = os.path.join(BASE_DIR, script_name)

    if not os.path.isfile(script_path):
        raise FileNotFoundError(f"Script not found: {script_path}")

    result = subprocess.run(
        [PYTHON, script_path],
        capture_output=True,
        text=True,
        timeout=1800,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Script failed: {script_name}\n"
            f"Exit code: {result.returncode}\n"
            f"stderr:\n{result.stderr}"
        )

    if result.stdout:
        print(result.stdout)


with DAG(
    dag_id="medical_data_pipeline",
    default_args=default_args,
    description="Daily ingestion of WHO and OpenFDA data into Snowflake",
    schedule="0 12 * * *",
    start_date=datetime(2026, 4, 28),
    catchup=False,
    tags=["medical", "etl", "snowflake"],
) as dag:

    collect_who = PythonOperator(
        task_id="collect_who_data",
        python_callable=run_script,
        op_args=["WHO_data_collection.py"],
    )

    clean_who = PythonOperator(
        task_id="clean_who_data",
        python_callable=run_script,
        op_args=["WHO_data_cleaning.py"],
    )

    collect_openfda = PythonOperator(
        task_id="collect_openfda_data",
        python_callable=run_script,
        op_args=["openFDA_data_colection.py"],
    )

    clean_openfda = PythonOperator(
        task_id="clean_openfda_data",
        python_callable=run_script,
        op_args=["openFDA_data_cleaning.py"],
    )

    load_snowflake = PythonOperator(
        task_id="load_to_snowflake",
        python_callable=run_script,
        op_args=["snowflakeLoader.py"],
    )

    run_dbt = BashOperator(
        task_id="run_dbt",
        bash_command="/home/airflow/.local/bin/dbt run --project-dir /opt/airflow/project/medical_dbt --profiles-dir /opt/airflow/project/medical_dbt",
    )

    collect_who >> clean_who >> load_snowflake
    collect_openfda >> clean_openfda >> load_snowflake
    load_snowflake >> run_dbt