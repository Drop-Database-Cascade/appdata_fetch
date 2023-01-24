import requests
import csv
from decouple import config
import pandas as pd
from pandas import DateOffset
import json
from pathlib import Path

#check country vs country code

#This script will loop though the music apps dictionary and conduct the following actions
# 1.    Send an API request for each country for both Android and Iphone

#Fetch API Key from local env
API_KEY = config('KEY')

# Input the variables that I'm trying to get data for (test variables)

#Master Parameters
beginning_date = '2021-01-01'
end_date = '2021-01-01'
metric_type = 'downloads'
load_type = 'F' # 'F' for Full or 'D' for Delta


#Define dictionary of possible combinations
music_apps = {
    "spotify": {
        "android": "com.spotify.music",
        "iphone": 324684580
    },
    "apple_music": {
        "android": "com.apple.android.music",
        "iphone": 1108187390
    },
    "resso_app": {
        "android": "com.moonvideo.android.resso",
        "iphone": 1457922673
    },
    "youtube_music": {
        "android": "com.google.android.apps.youtube.music",
        "iphone": 1017492454
    },
    "tidal_app": {
        "android": "com.aspiro.tidal",
        "iphone": 913943275
    },
    "amazon_app": {
        "android": "com.amazon.mp3",
        "iphone": 510855668
    },
    "deezer_app": {
        "android": "deezer.android.app",
        "iphone": 292738169
    },
    "soundcloud_app": {
        "android": "com.soundcloud.android",
        "iphone": 336353151
    },
    "gaana": {
        "android": "com.gaana",
        "iphone": 585270521
    },
    "wynk": {
        "android": "com.bsbportal.music",
        "iphone": 845083955
    }
}


def load_countries(app_name=str):
    country_list = []
    country_path = Path.cwd() / "input_files" / app_name / "countries_list.csv"
    with open(country_path, "r") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            country_list.append(row[0])
    return country_list
    
# Function Definition to get a request from the api
def request(app=str, metric=str, beg_date=str, end_date=str, country_code=str, device=str,api_key=str):
    acceptable_device_input = ['android', 'iphone']
    assert device in acceptable_device_input
    url = f"https://public-api.apptweak.com/api/public/store/apps/metrics/history.json?apps={app}&metrics={metric}&start_date={beg_date}&end_date={end_date}&country={country_code}&device={device}"

    headers = {
        "accept": "application/json",
        "x-apptweak-key": api_key
    }

    response = requests.get(url, headers=headers)

    return response.json()

# Load the JSON data

#data = {"result":{"835599320":{"downloads":[{"value":23,"date":"2022-01-01","precision":None},{"value":59,"date":"2022-01-02","precision":0.25},{"value":42,"date":"2022-01-03","precision":0.25}],"ratings":[{"value":None,"breakdown":None,"date":"2022-01-01"},{"value":None,"breakdown":None,"date":"2022-01-02"},{"value":None,"breakdown":None,"date":"2022-01-03"}]}},"metadata":{"request":{"path":"/api/public/store/apps/metrics/history.json","params":{"device":"android","country":"us","language":"us","start_date":"2022-01-01","end_date":"2022-01-03","apps":["835599320"],"metrics":["downloads","ratings"]},"cost":1,"max_credit_cost":613,"status":200},"response":None}}

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

def add_dim_cols(json_dict, df, cols=list, app=str):
    # Add new columns for apps, device, country, and language
    df['apps'] = list(json_dict['result'].keys())[0]
    for col in cols:
        dimension = json_dict['metadata']['request']['params'][col]
        df[col]= dimension
    # add date key columns
    df['date_key'] = df['date'].str.replace("-", "").astype(int)
    # add app name column
    df = df.assign(app_name=app)
    return df

# Write the DataFrame to a CSV file
def csv_write(df, app_name=str, counter=int, beginning_date=str, end_date=str):
    output_path = Path.cwd()/ "output_files" / app_name / f"{end_date}_to_{beginning_date}_{app_name}.csv"
    output_path.parent.mkdir(exist_ok=True, parents=True)
    if counter < 1:    
        df.to_csv(output_path, mode='w', index = False, header=True)
    else:
        df.to_csv(output_path, mode='a', index = False, header=False)
    return True


def create_watermark(app_name=str, end_date=str, beginning_date=str):
    sourceapp_output_file = Path.cwd()/ "output_files" / app_name / f"{end_date}_to_{beginning_date}_{app_name}.csv"
    sourceapp_output_file.parent.mkdir(exist_ok=True, parents=True)
    watermark_path = Path.cwd() / "output_files" / app_name / "watermark" / f"watermark_{app_name}.csv"
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

def combine_watermark(app_name=str, end_date=str, beginning_date=str, count=int):
    input_path = Path.cwd() / "output_files" / app_name / "watermark" / f"watermark_{app_name}.csv"
    #Read in input_path
    df = pd.read_csv(input_path)
    # output path
    output_path = Path.cwd()/ "output_files" / "master_watermark" / "combined_watermark.csv"
    if count < 1:    
        df.to_csv(output_path, mode='w', index = False, header=True)
    else:
        df.to_csv(output_path, mode='a', index = False, header=False)
    return True

def lookup_beginning_date(csv_path, apps, country, device):
    df = pd.read_csv(csv_path)
    try:
        next_end_date = df[(df['app_name'] == apps) & (df['country'] == country) & (df['device'] == device)]['date'].values[0] + pd.Timedelta('1 day')
        next_end_date = next_end_date.strftime('%Y-%m-%d')
    except:
        print(f"No watermark value for country code: {country}, therefore conducting full load from App Start Date")
        next_end_date = '2010-01-01'
    return next_end_date


def main():
#Set Variables
    
    #Fetch API Key from local env
    API_KEY = config('KEY')

    # Input the variables that I'm trying to get data for (test variables)

    #Master Parameters
    beginning_date = '2021-01-01'
    end_date = '2021-01-5'
    metric_type = 'downloads'
    load_type = 'F' # 'F' for Full or 'D' for Delta

    # Main Loop

    try:
        for app_name, devices in music_apps.items(): 
            # Set loop counter to be reset for each app
            count = 0  
            wm_count = 0       
            country_list = load_countries(app_name)  
            for country in country_list:
                for device, code in devices.items():

                    #Lookup end_date from watermark table 
                    if load_type == 'D':
                        csv_path = Path.cwd()/ "output_files" / "master_watermark" / "combined_watermark.csv"
                        beginning_date = lookup_beginning_date(csv_path, app_name, country, device)
                    elif load_type =='F':
                        pass
                    else:
                        raise Exception('Invalid load type provided')

                    api_response = request(code, metric_type, beginning_date, end_date, country, device, API_KEY)
                    print(api_response)
                    #api_response = {"result":{"com.spotify.music":{"downloads":[{"value":151880,"date":"2021-01-01","precision":0.25},{"value":143522,"date":"2021-01-02","precision":0.25},{"value":117403,"date":"2021-01-03","precision":0.25},{"value":101042,"date":"2021-01-04","precision":0.25},{"value":89371,"date":"2021-01-05","precision":0.25}]}},"metadata":{"request":{"path":"/api/public/store/apps/metrics/history.json","params":{"device":"android","country":"in","language":"in","start_date":"2021-01-01","end_date":"2021-01-05","apps":["com.spotify.music"],"metrics":["downloads"]},"cost":701,"max_credit_cost":701,"status":200},"response":None}}
                    #Extract downloads from request output
                    output_df = extract_metric_to_df(api_response, metric_type)
                
                    # Add additional columns for context
                    output_df = add_dim_cols(api_response, output_df, ['device', 'country', 'language'], app_name)
                    print(output_df)

                    #Write output to CSV
                    csv_write(output_df, app_name, count, beginning_date, end_date)
                    count += 1
                    break
                break
            #Get Watermark for each app
            create_watermark(app_name, end_date, beginning_date)

            #Combine all Watermark files together
            combine_watermark(app_name, end_date, beginning_date, wm_count)
            wm_count += 1
            break
       

        return True

    except Exception as e:
        raise e


if __name__ == "__main__":
    main()
    


#Set variable answer to the output of defined function, pass in variable app = app_name, metric = metric_name
#answer = request(app_name, metric_name, beginning_date, end_date, country_code, device, API_KEY)
#print(answer)

