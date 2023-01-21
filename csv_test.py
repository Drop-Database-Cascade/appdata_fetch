import requests
from decouple import config
import json
import csv

# Specify the app names, devices, and countries
api_key = config('KEY')
app_names = {'Spotify': ['com.spotify.music']}
metric_name = 'downloads'
beginning_date = '2022-01-01'
end_date = '2022-01-02'
country_codes = ['us']
devices = {'android': 'android'}

# seems to be missing headers in the below due to missing the json request and var 'headers' is never defined. In 'chatgpt_app_tweak
# _scripts.py, the following code is written to get the request from AppTweak API:
# Make an API request to App Tweak
#url = f"https://public-api.apptweak.com/api/public/store/apps/metrics/history.json?apps={device_app_name}&metrics={metric_name}%2Cratings&start_date={beginning_date}&end_date={end_date}&country={country_code}&device={device_code}"
#print(url)

#headers = {
#    "accept": "application/json",
#    "x-apptweak-key": "mEVu0O4Co6F1W1BcdGiofYHk4yo"
#}

#response = requests.get(url, headers=headers)

for app_name, device_app_names in app_names.items():
    for device, device_code in devices.items():
        for country_code in country_codes:
            device_app_name = device_app_names[0] if device == 'android' else device_app_names[1]

            #skip API call, copied in the data into var 'data' below:
            data = {'result': {'com.spotify.music': {'downloads': [{'value': 32508, 'date': '2022-01-01', 'precision': 0.25}, 
                {'value': 37452, 'date': '2022-01-02', 'precision': 0.25}], 'ratings': [{'value': 4.392, 'breakdown': 
                {'1': 2014638, '2': 775507, '3': 1014175, '4': 2561965, '5': 18262830, 'total': 24629115, 'avg': 4.392}, 
                'date': '2022-01-01'}, {'value': None, 'breakdown': None, 'date': '2022-01-02'}]}}, 'metadata': {'request': 
                {'path': '/api/public/store/apps/metrics/history.json', 
                'params': {'device': 'android', 'country': 'us', 'language': 'us', 'start_date': '2022-01-01', 'end_date': '2022-01-02', 
                'apps': ['com.spotify.music'], 'metrics': ['downloads', 'ratings']}, 'cost': 561, 'max_credit_cost': 562,'status': 200}, 
                'response': None}}
                
            print(data)
                        
            # Write the data to a CSV file
            path = "/Users/bmcca/Documents/app_tweak_repo/appdata_fetch/streaming_app_downloads/"
            with open(f'{path}{app_name}_{device}_{metric_name}_{beginning_date}_{end_date}_{country_code}.csv', 'w') as csv_file:
                fieldnames = ['app_name', 'device', 'date', 'downloads']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
            for item, in data:
                print(item)
                                
                writer.writerow({'app_name': app_name, 'device': device, 'date': item['date'], 'downloads': item['downloads']})
'''