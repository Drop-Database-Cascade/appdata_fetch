from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', 'etl_scripts')))
from app_metric_fetch import main as app_metric_fetch
from dim_country import main as dim_country
from dim_date import main as dim_date

# Define default_args dictionary to pass to the DAG
default_args = {
    'owner': 'me',
    'start_date': datetime(2022, 1, 1),
    'depends_on_past': False,
    'retries': 0
}

# Create a DAG instance
dag = DAG(
    'app_metrics_ETL', default_args=default_args, schedule_interval=None
)

# Define the Dim Country task using the PythonOperator
dim_country_load = PythonOperator(
    task_id='load_dim_country',
    python_callable=dim_country,
    dag=dag
)

# Define the Dim Date task using the PythonOperator
dim_date_load = PythonOperator(
    task_id='load_dim_date',
    python_callable=dim_date,
    dag=dag
)


# Define the app_metric_fetch task using the PythonOperator
fetch_metrics = PythonOperator(
    task_id='fetch_metrics_all_apps',
    python_callable=app_metric_fetch,
    dag=dag,
)

#Define Relationships
[dim_country_load, dim_date_load] >> fetch_metrics

