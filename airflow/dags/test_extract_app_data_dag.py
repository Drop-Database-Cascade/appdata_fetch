#This file contains the dag which runs the pytest module for each of the classes called for the extract app data dag. Class tested are as follows:
# local_file_operations_class
# dim_table_class
# app_metrics_request_class
# app_metrics_local_file_operations_class


from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', 'testing')))
testing_path = '$AIRFLOW_HOME/../testing/'

# Define default_args dictionary to pass to the DAG
default_args = {
    'owner': 'me',
    'start_date': datetime(2022, 1, 1),
    'depends_on_past': False,
    'retries': 0
}

# Create a DAG instance
dag = DAG(
    'test_app_metrics_ETL', default_args=default_args, schedule_interval=None
)


# Define the test tasks using the BashOperator, each operator calls pytest unit testing on the app_data_fetch app functions
test_local_file_operations = BashOperator(
        task_id=f'run_pytest_test_local_file_operations_class_test',
        bash_command=f'pytest {testing_path}test_local_file_operations_class_test.py',
        dag=dag
    )

test_dim_table_class = BashOperator(
        task_id=f'run_pytest_test_dim_table_class',
        bash_command=f'pytest {testing_path}test_dim_table_class.py',
        dag=dag
    )

test_app_metrics_request = BashOperator(
        task_id=f'run_pytest_test_app_metrics_request',
        bash_command=f'pytest {testing_path}test_app_metrics_request.py',
        dag=dag
    )

test_app_metrics_local_file_operations = BashOperator(
        task_id=f'run_pytest_test_app_metrics_local_file_operations',
        bash_command=f'pytest {testing_path}test_app_metrics_local_file_operations.py',
        dag=dag
    )

#Define Relationships
test_local_file_operations >> [test_app_metrics_request, test_dim_table_class, test_app_metrics_local_file_operations] 

