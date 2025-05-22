from airflow import DAG
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 5, 10),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'transform_glue_dag2',
    default_args=default_args,
    schedule_interval='@once',
    catchup=False  # Prevent backfilling
)

# Python function to check the XCom value for task status
def check_openweather_api_status(**kwargs):
    ti = kwargs['ti']
    task_status = ti.xcom_pull(dag_id='openweather_api_dag1', task_ids='extract_api_data', key='task_status')
    
    if task_status == 'success':
        print("First DAG task completed successfully. Proceeding with Glue transformation.")
        return 'success'
    else:
        print("First DAG task failed. Skipping Glue transformation.")
        return 'failed'

# Check task status before running Glue job
check_status_task = PythonOperator(
    task_id='check_openweather_api_status',
    python_callable=check_openweather_api_status,
    provide_context=True,
    dag=dag,
)

# Glue job task (run only if the first task succeeded)
transform_task = GlueJobOperator(
    task_id='transform_task',
    job_name='script',
    script_location='s3://aws-glue-assets-767828728592-ap-south-1/scripts/script.py',
    s3_bucket='aws-glue-assets-767828728592-ap-south-1',
    aws_conn_id='AWS_CONN',
    region_name='ap-south-1',
    iam_role_name='airflow-clean-iam-pratical',
    dag=dag
)

# Set task dependencies
check_status_task >> transform_task
