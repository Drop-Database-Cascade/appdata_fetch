#This file contains the main dag pipeline used extract data from the AppTweak Api. The tasks are as follows:
# 1.    Check Total Credit Costs - calculates the expected cost of the API request and writes output to expected cost output folder.
#       if cost > budget (Airflow user input) pipeline is failed
# 2.    Create Date Dim table - create a date dimension csv table (overwrite) - daily from 2010 to end date (Airflow Input)
# 3.    Create Country Dim table - maps all possible AppTweak Country codes to their repective full country name.
# 4.    Fetch Metrics All Apps - Based on user input files (Country List CSVs, Music Apps python file) & Airflow Variables,
#       Sends requests to the AppTweak Api and writes the output to csv files in the respective output folders.
#       Dag order is run as follows: check_api_costs >> [dim_country_load, dim_date_load] >> fetch_metrics

from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os, sys
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', 'etl_scripts')))

#Import Task Funtions
from app_metric_fetch import app_metrics_fetch as app_metric_fetch
from dim_country import main as dim_country
from dim_date import get_date_dim as dim_date
from app_metric_cost import check_total_credit_cost


#Get variables from Airflow Database
metric_type = json.loads(Variable.get("app_metric_fetch_config"))["metric_type"]
load_type = json.loads(Variable.get("app_metric_fetch_config"))["load_type"]
end_date = json.loads(Variable.get("app_metric_fetch_config"))["end_date"]
budget = json.loads(Variable.get("app_metric_fetch_config"))["budget"]
demo_flag = int(Variable.get("demo_flag", default_var=1))

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
    op_args=[end_date],
    dag=dag
)

# Define the app_metric_fetch task using the PythonOperator
fetch_metrics = PythonOperator(
    task_id='fetch_metrics_all_apps',
    python_callable=app_metric_fetch,
    provide_context=True,
    op_args=[metric_type, load_type, end_date, demo_flag],
    dag=dag,
)

# Define the app_metric_cost task using the PythonOperator
check_api_costs = PythonOperator(
    task_id='check_total_credit_cost',
    python_callable=check_total_credit_cost,
    provide_context=True,
    op_args=[metric_type, end_date, load_type, budget],
    dag=dag,
)

#Define Relationships
check_api_costs >> [dim_country_load, dim_date_load] >> fetch_metrics

