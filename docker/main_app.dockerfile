FROM python:3.9-slim

# Set environment variables

ENV AIRFLOW_HOME=/appdata_fetch_app/airflow

#Setting to  port 5433 to match postgrea container config
ENV AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@airflow_postgres:5432/airflow

ENV AIRFLOW__CORE__EXECUTOR=LocalExecutor
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False

#Get Project Root Variable
ENV PROJECT_ROOT_PATH=/appdata_fetch_app

#Get API_KEY Variable from docker compose or manual passing
ENV API_KEY ${API_KEY}

# install psycopg2 dependencies
RUN apt-get update \
    && apt-get -y install libpq-dev gcc

# Install general dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r /tmp/requirements.txt

# Copy ETL & Testing Scripts
COPY etl_scripts/ /appdata_fetch_app/etl_scripts
COPY testing/ /appdata_fetch_app/testing

# Copy DAGs
COPY airflow/dags/ /appdata_fetch_app/airflow/dags/


# Copy the entrypoint script
COPY /docker/main_app_entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose the web server port
EXPOSE 8080

# Start the web server and scheduler
ENTRYPOINT ["/entrypoint.sh"]