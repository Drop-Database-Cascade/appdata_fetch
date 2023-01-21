import requests
import json
import csv

# Specify the app names, devices, and countries
app_names = {'Spotify': ['com.spotify.music', '324684580']}
metric_name = 'downloads'
beginning_date = '2022-01-01'
end_date = '2022-01-02'
country_codes = ['us']
devices = {'android': 'android', 'iphone': 'iphone'}


'''
for app_name, device_app_names in app_names.items():
    for device, device_code in devices.items():
        for country_code in country_codes:
            device_app_name = device_app_names[0] if device == 'android' else device_app_names[1]
            # Make an API request to App Tweak
            url = f"https://public-api.apptweak.com/api/public/store/apps/metrics/history.json?apps={device_app_name}&metrics={metric_name}%2Cratings&start_date={beginning_date}&end_date={end_date}&country={country_code}&device={device_code}"
            print(url)
            
            headers = {
                "accept": "application/json",
                "x-apptweak-key": "mEVu0O4Co6F1W1BcdGiofYHk4yo"
            }
            
            response = requests.get(url, headers=headers)
            data = response.json()
        
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
                    

