#!/bin/bash

# Initialize the database
airflow db init

#Create Default User
airflow users create -r Admin -u admin -e admin@admin.com -f Airflow -l Admin -p admin

# Set airflow default variables
airflow variables set app_metric_fetch_config '{"metric_type": "downloads", "load_type": "F", "beginning_date": "2021-01-01", "end_date": "2022-01-02", "budget": 10000}'

# Start the web server
airflow webserver -p 8080 &

# Start the scheduler
airflow scheduler;
