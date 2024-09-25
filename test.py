from airflow import DAG
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.operators.gcs import GCSCopyObjectOperator, GCSDeleteObjectOperator
from datetime import datetime, timedelta
import os

# Define default_args for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 9, 20),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Initialize the DAG
with DAG(
    'move_local_files_to_gcs_and_between_buckets',
    default_args=default_args,
    description='DAG to move local files to GCS and then from one GCS bucket to another',
    schedule_interval=timedelta(days=1),
) as dag:

    # Define the local folder and GCS bucket names
    local_folder = '/path/to/local/folder'  # Replace with your local folder path
    source_bucket = 'source-bucket-name'  # Replace with your source GCS bucket name
    destination_bucket = 'destination-bucket-name'  # Replace with your destination GCS bucket name

    # Task to upload local files to GCS
    local_files = os.listdir(local_folder)  # List files in the local directory
    for file_name in local_files:
        upload_task = LocalFilesystemToGCSOperator(
            task_id=f'upload_{file_name}',
            src=os.path.join(local_folder, file_name),  # Local file path
            dst=file_name,  # Destination file name in GCS
            bucket=source_bucket,  # GCS bucket name
        )

        # Task to move the file from the source bucket to the destination bucket
        copy_task = GCSCopyObjectOperator(
            task_id=f'copy_{file_name}',
            source_bucket=source_bucket,
            source_object=file_name,
            destination_bucket=destination_bucket,
            destination_object=file_name,
            move_object=False,  # Set to False for copy operation
        )

        # Task to delete the file from the source bucket after copying
        delete_task = GCSDeleteObjectOperator(
            task_id=f'delete_{file_name}',
            bucket=source_bucket,
            object_name=file_name,
            trigger_rule='all_success',  # Only run if the copy task succeeded
        )

        # Set task dependencies
        upload_task >> copy_task >> delete_task
