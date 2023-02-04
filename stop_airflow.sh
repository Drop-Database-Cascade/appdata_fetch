#!/bin/bash

echo "Stopping Airflow Webserver..."
pkill -f "airflow webserver"

echo "Stopping Airflow Scheduler..."
pkill -f "airflow scheduler"

echo "Airflow Webserver and Scheduler stopped!"