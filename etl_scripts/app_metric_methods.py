#This file contains the AppMetrics Class and corresponding functions used to interact with the App Tweak API.
import requests
import csv
import pandas as pd
from pandas import DateOffset
import json
from pathlib import Path

class AppMetrics:
    def __init__(self, app_name=str, API_KEY=str, beginning_date=str, end_date=str, metric_name=str):
        self.app_name = app_name
        self.api_key = API_KEY
        self.beginning_date = beginning_date   #used as default value for the beginning date lookup
        self.end_date = end_date
        self.metric_name = metric_name
        
    def load_countries(self):
        #load countries into a list based on input config file
        country_list = []
        country_path = Path.cwd() / "data" / "input_files" / self.app_name / "countries_list.csv"
        with open(country_path, "r") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                country_list.append(row[0])
        return country_list

    def lookup_beginning_date(self, csv_path, country, device):
        df = pd.read_csv(csv_path)
        try:
            next_end_date = df[(df['app_name'] == self.app_name) & (df['country'] == country) & (df['device'] == device)]['date'].values[0] + pd.Timedelta('1 day')
            next_end_date = next_end_date.strftime('%Y-%m-%d')
        except:
            print(f"No watermark value for country code: {country}, therefore conducting full load from App Start Date")
            # set default date
            next_end_date = self.beginning_date
        return next_end_date
        
    def request(self, app=str, beg_date=str, country_code=str, device=str):
        acceptable_device_input = ['android', 'iphone']
        assert device in acceptable_device_input
        url = f"https://public-api.apptweak.com/api/public/store/apps/metrics/history.json?apps={app}&metrics={self.metric}&start_date={beg_date}&end_date={self.end_date}&country={country_code}&device={device}"

        headers = {
            "accept": "application/json",
            "x-apptweak-key": self.api_key
        }

        response = requests.get(url, headers=headers)

        return response.json()

    # Load the JSON data

    #data = {"result":{"835599320":{"downloads":[{"value":23,"date":"2022-01-01","precision":None},{"value":59,"date":"2022-01-02","precision":0.25},{"value":42,"date":"2022-01-03","precision":0.25}],"ratings":[{"value":None,"breakdown":None,"date":"2022-01-01"},{"value":None,"breakdown":None,"date":"2022-01-02"},{"value":None,"breakdown":None,"date":"2022-01-03"}]}},"metadata":{"request":{"path":"/api/public/store/apps/metrics/history.json","params":{"device":"android","country":"us","language":"us","start_date":"2022-01-01","end_date":"2022-01-03","apps":["835599320"],"metrics":["downloads","ratings"]},"cost":1,"max_credit_cost":613,"status":200},"response":None}}

    def extract_metric_to_df(self, json_dict):
        # Extract the downloads data
        metric = json_dict['result'][list(json_dict['result'].keys())[0]][self.metric_name]
        # Create a DataFrame from the metric data
        metric_df = pd.DataFrame(metric)
        # Rename the columns
        metric_df = metric_df.rename(columns={'value': self.metric_name})
        metric_df = metric_df.drop('precision', axis=1)
        metric_df = metric_df.dropna(subset=[self.metric_name])
        return metric_df

    def add_dim_cols(self, json_dict, df, cols=list):
        # Add new columns for apps, device, country, and language
        df['apps'] = list(json_dict['result'].keys())[0]
        for col in cols:
            dimension = json_dict['metadata']['request']['params'][col]
            df[col]= dimension
        # add date key columns
        df['date_key'] = df['date'].str.replace("-", "").astype(int)
        # add app name column
        df = df.assign(app_name=self.app_name)
        return df

    # Write the DataFrame to a CSV file
    def csv_write(self, df, counter=int, beginning_date=str):
        output_path = Path.cwd()/ "data" / "output_files" / self.app_name / f"{self.end_date}_to_{beginning_date}_{self.app_name}.csv"
        output_path.parent.mkdir(exist_ok=True, parents=True)
        if counter < 1:    
            df.to_csv(output_path, mode='w', index = False, header=True)
        else:
            df.to_csv(output_path, mode='a', index = False, header=False)
        return True


    def create_watermark(self, beginning_date=str):
        sourceapp_output_file = Path.cwd()/ "data" / "output_files" / self.app_name / f"{self.end_date}_to_{beginning_date}_{self.app_name}.csv"
        sourceapp_output_file.parent.mkdir(exist_ok=True, parents=True)
        watermark_path = Path.cwd() / "data" / "output_files" / self.app_name / "watermark" / f"watermark_{self.app_name}.csv"
        watermark_path.parent.mkdir(exist_ok=True, parents=True)
        df = pd.read_csv(sourceapp_output_file)
        # drop all columns except for 'apps', 'country_code', 'device_name' and 'date'
        df = df.drop(columns=[col for col in df.columns if col not in ['app_name', 'country', 'device', 'date']], axis=1)
        df["date"] = pd.to_datetime(df["date"])
        df_watermark = df.groupby(['app_name','country','device'], as_index=False)['date'].max()
        print(df_watermark)
        df_watermark['date'] = df['date'].dt.strftime("%Y-%m-%d")
        df_watermark.to_csv(watermark_path, mode='w', index = False, header=True)
        return True

    def combine_watermark(self, count=int):
        input_path = Path.cwd() / "data" / "output_files" / self.app_name / "watermark" / f"watermark_{self.app_name}.csv"
        #Read in input_path
        df = pd.read_csv(input_path)
        # output path
        output_path = Path.cwd()/ "data" / "output_files" / "master_watermark" / "combined_watermark.csv"
        if count < 1:    
            df.to_csv(output_path, mode='w', index = False, header=True)
        else:
            df.to_csv(output_path, mode='a', index = False, header=False)
        return True