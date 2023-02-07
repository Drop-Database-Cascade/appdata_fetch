#!/bin/bash

# Initialize the database
airflow initdb

# Start the web server
airflow webserver -p 8080 &

# Start the scheduler
airflow scheduler

# Set airflow default variables
airflow variables --set app_metric_fetch_config '{"metric_type": "downloads", "load_type": "F", "beginning_date": "2021-01-01", "end_date": "2022-01-02", "budget": 10000}';
