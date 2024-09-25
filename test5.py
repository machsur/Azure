from airflow import models
from datetime import datetime, timedelta
from airflow.operators.bash import BashOperator

# Define the DAG's default arguments
default_args = {
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with models.DAG(
    'gsutil_command_example',
    default_args=default_args,
    description='Execute gsutil command using Cloud Composer',
    schedule_interval=datetime(2024, 9, 20),  # Set to None to run the DAG manually
    catchup=False
) as dag:
    
    # Use BashOperator to execute a gsutil command
    upload_file_to_gcs = BashOperator(
        task_id='upload_file_to_gcs',
        bash_command='gsutil cp /home/airflow/gcs/data/file.txt gs://your-target-bucket/path/in/gcs/file.txt'
        )
    
    upload_file_to_gcs
