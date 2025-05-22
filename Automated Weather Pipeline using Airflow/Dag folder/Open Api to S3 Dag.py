from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.s3 import S3CreateObjectOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import pandas as pd
import requests

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 5, 10),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('openweather_api_dag1', default_args=default_args, schedule_interval="@once", catchup=False)

# Set your OpenWeather API endpoint and parameters
api_endpoint = "https://api.openweathermap.org/data/2.5/forecast"
api_params = {
    "q": "Toronto,Canada",
    "appid": Variable.get("key")
}

def extract_openweather_data(**kwargs):
    try :

        print("Extracting started ")
        ti = kwargs['ti']
        response = requests.get(api_endpoint, params=api_params)
        data = response.json()
        print(data)
        df = pd.json_normalize(data['list'])
        print(df)
        ti.xcom_push(key='final_data', value=df.to_csv(index=False))
        ti.xcom_push(key='task_status', value='success')
        print("Data extraction successful.")
    except Exception as e:
        print(f"Data extraction failed: {e}")
        ti.xcom_push(key='task_status', value='failed')

extract_api_data = PythonOperator(
    task_id='extract_api_data',
    python_callable=extract_openweather_data,
    provide_context=True,
    dag=dag,
)

upload_to_s3 = S3CreateObjectOperator(
    task_id="upload_to_S3",
    aws_conn_id='AWS_CONN',
    s3_bucket='airflow-pratical',
    s3_key='files/weather_api_data.csv',
    data="{{ ti.xcom_pull(key='final_data') }}",
    replace = True,
    dag=dag,
)

# Set task dependencies
extract_api_data >> upload_to_s3
