#!/bin/bash

if [ -z "$VIRTUAL_ENV" ]; then
    # activate virtual env
    source /home/mfifield/getmusicapps/bin/activate
    echo "venv activated..."
else
    echo "Virtual environment already activated"
fi

echo "Starting Airflow Webserver..."
nohup airflow webserver -p 8080 > webserver.log 2>&1 &

echo "Starting Airflow Scheduler..."
nohup airflow scheduler > scheduler.log 2>&1 &

echo "Airflow Webserver and Scheduler started!"