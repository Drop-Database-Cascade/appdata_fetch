#This file contains the classes and corresponding functions used to interact with the App Tweak API or store outputs locally.
import requests
import pandas as pd
import os
from datetime import datetime, timedelta

#Import Parent Class
from local_file_operations_class import local_file_operations

class app_metrics_requests:
# Fetches API Key from the config file. Contains methods to independently fetch and interact with App Tweak API. All methods to manipulate the output are pandas based.


    def __init__(self, app_name:str, beginning_date:str, end_date:str, metric_name:str):

        assert metric_name in ['downloads', 'ratings', 'app-power', 'ratings', 'daily-ratings']
        assert datetime.strptime(end_date, "%Y-%m-%d") > datetime.strptime(beginning_date, "%Y-%m-%d")

        #Def Parent variables - Updated API to be passed in from dockerfile
        self.app_name = app_name
        self.api_key = os.environ.get("API_KEY")
        self.beginning_date = beginning_date   #used as default value for the beginning date lookup
        self.end_date = end_date
        self.metric_name = metric_name

    #send request to App Tweak Api and receive response in JSON format.
    def request(self, app:str, beg_date:str, country:str, device=str):
        acceptable_device_input = ['android', 'iphone']
        assert device in acceptable_device_input
        url = f"https://public-api.apptweak.com/api/public/store/apps/metrics/history.json?apps={app}&metrics={self.metric_name}&start_date={beg_date}&end_date={self.end_date}&country={country}&device={device}"

        headers = {
            "accept": "application/json",
            "x-apptweak-key": self.api_key
        }

        response = requests.get(url, headers=headers)

        return response.json()

    #Convert JSON output to df and drop null records if applicable
    def extract_metric_to_df(self, json_dict:dict):
        # Extract the downloads data
        metric = json_dict['result'][list(json_dict['result'].keys())[0]][self.metric_name]
        # Create a DataFrame from the metric data
        metric_df = pd.DataFrame(metric)
        # Rename the columns
        metric_df = metric_df.rename(columns={'value': self.metric_name})
        metric_df = metric_df.drop('precision', axis=1)
        metric_df = metric_df.dropna(subset=[self.metric_name])
        return metric_df
    
    #Add additional columns for context, including a date key that can reference a date dimension table
    def add_dim_cols(self, json_dict:dict, df, cols:list):
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
    
    # Calculate the cost of an API request in credits
    def calculate_total_credit_cost(self, matrix:dict, beginning_date:str):
        base_credit_cost = matrix["App Metrics"][self.metric_name]["base_credit_cost"]
        extra_credit_cost = matrix["App Metrics"][self.metric_name]["extra_credit_cost_per_day"]
        beginning_date = datetime.strptime(beginning_date, "%Y-%m-%d")
        end_date = datetime.strptime(self.end_date, "%Y-%m-%d")
        days = (end_date - beginning_date).days + 1
        total_credit_cost = base_credit_cost + extra_credit_cost * max(0, days - 1)
        return total_credit_cost
    
    #Validate the cost of a request will meet budget requirements
    def check_cost_budget(self, budget:int, total_cost:int):
        if budget < total_cost:
            raise ValueError("Budget is less than total cost")
        else:
            return True
    

class app_metrics_local_file_operations(local_file_operations, app_metrics_requests):

    def __init__(self, app_name:str, beginning_date:str, end_date:str, metric_name:str):
        local_file_operations.__init__(self)
        app_metrics_requests.__init__(self, app_name, beginning_date, end_date, metric_name)

        #Initialise common file paths
        self.app_data_csv_output = os.path.join(self.output_path, self.app_name , f"{self.end_date}_{self.app_name}.csv")
        self.local_watermark_path = os.path.join(self.output_path, self.app_name , "watermark", f"watermark_{self.app_name}.csv")
        self.combined_watermark_path = os.path.join(self.output_path, "master_watermark", "combined_watermark.csv")

    # Write the Output DataFrame to a CSV file
    def csv_write(self, df, counter:int):
        output_path = self.app_data_csv_output
        if counter < 1:    
            df.to_csv(output_path, mode='w', index = False, header=True)
        else:
            df.to_csv(output_path, mode='a', index = False, header=False)
        return True

    #Create a Watermark table for each country and save locally
    def create_watermark(self):
        sourceapp_output_file = self.app_data_csv_output
        watermark_path = self.local_watermark_path
        df = pd.read_csv(sourceapp_output_file)
        # drop all columns except for 'apps', 'country_code', 'device_name' and 'date'
        df = df.drop(columns=[col for col in df.columns if col not in ['app_name', 'country', 'device', 'date']], axis=1)
        df["date"] = pd.to_datetime(df["date"])
        df_watermark = df.groupby(['app_name','country','device'], as_index=False)['date'].max()
        df_watermark['date'] = df['date'].dt.strftime("%Y-%m-%d")
        df_watermark.to_csv(watermark_path, mode='w', index = False, header=True)
        return True
    
    #Combine the watermark tables for each country into a single table
    def combine_watermark(self, count:int):
        input_path = self.local_watermark_path
        #Read in input_path
        df = pd.read_csv(input_path)
        # output path
        output_path = self.combined_watermark_path
        if count < 1:    
            df.to_csv(output_path, mode='w', index = False, header=True)
        else:
            df.to_csv(output_path, mode='a', index = False, header=False)
        return True
    
    #Lookup the beginning date for a particular country from the master watermark table
    def lookup_beginning_date(self, country:str):
        df = pd.read_csv(self.combined_watermark_path)
        try:
            next_end_date = df[(df['app_name'] == self.app_name) & (df['country'] == country)]['date'].values
            if len(next_end_date) == 0:
                next_end_date = self.beginning_date
                return next_end_date
            else:
                next_end_date = next_end_date[0]
                print(next_end_date)
            next_end_date = datetime.strptime(next_end_date, '%Y-%m-%d') + timedelta(days=1)
            next_end_date = next_end_date.strftime('%Y-%m-%d')
            print(self. beginning_date)
        except Exception as e:
            raise(e)
        return next_end_date
    
    #Check the load type parameter and refer to the watermark table to set the beginning date if load type is Delta (D)
    def check_beg_date(self, load_type:str, country:str):
        if load_type == 'D':
            beginning_date = self.lookup_beginning_date(country)
        elif load_type == 'F':
            beginning_date = self.beginning_date
        else:
            raise Exception('Invalid load type provided')
        return beginning_date

    