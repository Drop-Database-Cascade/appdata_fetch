import requests
from decouple import config
import pandas as pd
import json

#Fetch API Key from local env
API_KEY = config('KEY')

# Input the variables that I'm trying to get data for (test variables)
app_name = "835599320"
metric_name = "downloads"
beginning_date = "2022-01-01"
end_date = "2022-01-03"
country_code = "us"
device = "android"

# Function Definition to get a request from the api
def request(app=str, metric=str, beg_date=str, end_date=str, country_code=str, device=str,api_key=str):
    acceptable_device_input = ['android', 'iphone']
    assert device in acceptable_device_input
    url = f"https://public-api.apptweak.com/api/public/store/apps/metrics/history.json?apps={app}&metrics={metric}%2Cratings&start_date={beg_date}&end_date={end_date}&country={country_code}&device={device}"

    headers = {
        "accept": "application/json",
        "x-apptweak-key": api_key
    }

    response = requests.get(url, headers=headers)

    return response.text

# Load the JSON data

data = {"result":{"835599320":{"downloads":[{"value":23,"date":"2022-01-01","precision":None},{"value":59,"date":"2022-01-02","precision":0.25},{"value":42,"date":"2022-01-03","precision":0.25}],"ratings":[{"value":None,"breakdown":None,"date":"2022-01-01"},{"value":None,"breakdown":None,"date":"2022-01-02"},{"value":None,"breakdown":None,"date":"2022-01-03"}]}},"metadata":{"request":{"path":"/api/public/store/apps/metrics/history.json","params":{"device":"android","country":"us","language":"us","start_date":"2022-01-01","end_date":"2022-01-03","apps":["835599320"],"metrics":["downloads","ratings"]},"cost":1,"max_credit_cost":613,"status":200},"response":None}}

def extract_metric_to_df(json_dict, metric_name=str):
    # Extract the downloads data
    metric = json_dict['result'][list(json_dict['result'].keys())[0]][metric_name]
    # Create a DataFrame from the metric data
    metric_df = pd.DataFrame(metric)
    # Rename the columns
    metric_df = metric_df.rename(columns={'value': metric_name})
    metric_df = metric_df.drop('precision', axis=1)
    metric_df = metric_df.dropna(subset=[metric_name])
    return metric_df

# cols = ['device', 'country', 'language']
def add_dim_cols(json_dict, df, cols=list):
    # Add new columns for apps, device, country, and language
    df['apps'] = list(json_dict['result'].keys())[0]
    for col in cols:
        dimension = json_dict['metadata']['request']['params'][col]
        df[col]= dimension
    df['date_key'] = df['date'].str.replace("-", "").astype(int)
    return df

# Write the DataFrame to a CSV file
def csv_write(df, path, counter=int):
    if counter < 1:    
        df.to_csv(path, mode='w', index = False, header=True)
    else:
        df.to_csv(path, mode='a', index = False, header=False)
    return True


def main():
    try:
        # Set loop counter to be used later and path
        count = 0
        path = '\spotify_downloads\Output\downloads_summary.csv'

        #Extract downloads from request output
        output_df = extract_metric_to_df(data, 'downloads')
        print(output_df)

        # Add additional columns for context
        output_df = add_dim_cols(data, output_df, ['device', 'country', 'language'])
        print(output_df)

        #Write output to CSV
        csv_write(output_df, path, count)
        count += 1
        return True

    except Exception as e:
        return False

main()
    


#Set variable answer to the output of defined function, pass in variable app = app_name, metric = metric_name
#answer = request(app_name, metric_name, beginning_date, end_date, country_code, device, API_KEY)
#print(answer)

