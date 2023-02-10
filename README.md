# AppTweak API Data Fetch using Airflow

## Overview
This project is designed to run Airflow ETL pipelines and its dependencies in a containerized environment using Docker and Docker Compose. The application has three services: `airflow_postgres`, `seed_data`, and `main_app`. The main application is designed to extract data from the AppTweak Api (specifically App Metrics) service in a managed and repeatable way to minimise overhead and costs. Key metrics on both android and iphone apps are retrieved based on user defined inputs and saved into an output folder in csv format. The use-case this application was built around was to extract and compare download metrics over time for the top music apps globally (Spotify, Soundcloud etc..)  This application supports both loading all metrics from a specific date & automated logic to load all data from the last load conducted using a date benchmark (watermark).

More info on the AppTweek Api data source is available here: https://developers.apptweak.com/reference/app-metrics

## Requirements
- Docker
- Docker Compose
- WSL 2 recommended if running docker on Windows (due to certain bugs with mounting container volumns locally)

## Services

### airflow_postgres
This service runs a PostgreSQL database for use with Apache Airflow. The database is built using the `docker/airflow_postgres.dockerfile` and is exposed on port 5433 for the local machine and 5432 for other containers in the docker network. The environment variables `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` are set to `airflow`, `airflow`, and `airflow` respectively. The database data is persisted in a volume named `postgres-data`.

### seed_data
This service seeds the data for the main application. The data is built using the `docker/seed_data.dockerfile` and is mapped to the host directory `${HOST_FILE_DIR-/mnt/c/apptweak_api}/data` at `/appdata_fetch_app/data`.

### main_app
This service is the main application. It is built using the `docker/main_app.dockerfile` and exposed on port 8080. This service depends on the `airflow_postgres` and `seed_data` services and maps the host directory `${HOST_FILE_DIR-/mnt/c/apptweak_api}/data` at `/appdata_fetch_app/data`. The API_KEY required for this app should be stored in a `.env` file saved in the project root. The Main Airflow App consists of two dags: extract_app_data_ETL and test_extract_app_data_ETL.

extract_app_data_ETL does the following:

    1. Check Total Credit Costs: Calculates the expected cost of the API request and writes the output to the expected cost output folder. If the cost is greater than the budget (Airflow user input), the pipeline is failed.
    2. Create Date Dim table: Creates a date dimension CSV table (overwrite) on a daily basis from 2010 to the end date (Airflow input).
    3. Create Country Dim table: Maps all possible AppTweak country codes to their respective full country names.
    4. Fetch Metrics All Apps: Based on user-input files (country list CSVs, music apps Python file) and Airflow variables, sends requests to the AppTweak API and writes the output to CSV files in the respective output folders. The DAG order is run as follows: check_api_costs >> [dim_country_load, dim_date_load] >> fetch_metrics.

test_extract_app_data_ETL does the following:
1. Use pytest to unit test each of the class methods used by the extract_app_data_ETL dag.

## How to get started
1. Clone this repository.
2. Navigate to the root directory of the repository.
3. Set your AppTweak API Key in your .env file as API_KEY
4. Optionally set your volume mounted directory (this is )
5. Run `docker-compose up` to start all services.
6. Access the application in your web browser at `http://localhost:8080`.
7. Login using the default username:admin and password:admin

## How to configure for your requirements
1. Check container bound directories to check that they were created correctly.
2. Edit the input files, to suit your data request requires. Edit beginning dates per app in the music_apps.py file (defaults are set to the earliest available date) & add/remove apps as required.
Edit the countries list csv for each app, this is the country list that gets looped through for api removes. Add/remove as needed.
3. Edit Airflow variables through the UI in the web browser, the main variables are stored as a dictionary with the key App_Metric_Fetch Config. Make sure to set the demo flag to 0 (stored as a separate variable).
4. Run app_metrics_ETL_test to test your environment variables are set correctly and functions are working as expected (optional)
5. Run the app_metrics_ETL and access your output files in the volume mounted output directory on your local machine

## Airflow Vars
- metric_type: this is the type of metric to be requested from the API, see apptweak documentation for more details
- load_type: Choose to either do a Full Load (F) from dates listed in the music_apps.py file or a Delta Load (D) which automatically loads data from the last load run (references the combined watermark file).
- beginning_date: Default beginning date if the relevant watermark date can't be found in a Delta Load (D). Not used for Full Loads (F) but must still be specified.
- end_date: The end date that you want data to be requested up until.
- budget: This is the amount of AppTweak credits you are willing to spend, the main dag will run a check to calculate if the total cost of the API request will exceed your budget and fail the pipeline if so.
- demo_flag: 1 for true, 0 for False - If set to true, will run the app_metrics_ETL pipeline using dummy data and only loop through 1 app, 1 country, 1 device. This will not send an API request and allows a safe integration test.



## Notes
- The `postgres-data` volume is created using the local driver.
- The host directory for data mapping can be overridden by setting the `HOST_FILE_DIR` environment variable.
- This app was developed using WSL Ubuntu distribution for windows, other OS configurations have not been tested.
- If using windows, it's recommended you run docker compose from the project root using WSL terminal (Ubuntu) - it's recommended you set the HOST_FILE_DIR to a path in /mnt/c/... so that you can interact with the input and output files using windows programs. This was tested to be the most effective and reliable configuration. Once docker compose has been run, you may find it convenient to start and stop the container app using Docker Desktop in Windows. 
- Using the AppTweak API requires that you create an account with AppTweak API. Large data requests can be quite expensive - use at your own risk.

