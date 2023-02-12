#!/bin/bash

# Initialize the database
airflow db init

#Create Default User
airflow users create -r Admin -u admin -e admin@admin.com -f Airflow -l Admin -p admin

# Set airflow default variables
VAR_EXISTS=`airflow variables get app_metric_fetch_config`
if [ -z "$VAR_EXISTS" ]; then
    airflow variables set --description "The configuration used for the app_metric_fetch operation" \
    app_metric_fetch_config '{"metric_type": "downloads", "load_type": "F", "beginning_date": "2021-01-01", "end_date": "2022-01-02", "budget": 10000}'
fi

VAR_EXISTS=`airflow variables get demo_flag`
if [ -z "$VAR_EXISTS" ]; then
    airflow variables set --description "Flag to indicate whether to run in demo mode" \
    demo_flag 1
fi


# Start the web server
airflow webserver -p 8080 &

# Start the scheduler
airflow scheduler;
