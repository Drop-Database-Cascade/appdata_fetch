import requests

# Input the variables that I'm trying to get data for
app_name = "835599320" #App ID is operating specific
metric_name = "downloads"
beginning_date = "2022-01-01"
end_date = "2022-12-31"
country_code = "us"
device = "iphone"

# Function Definition to get a request from the api
def request(app=str, metric=str, beg_date=str, end_date=str, country_code=str, device=str):
    acceptable_device_input = ['android', 'iphone']
    assert device in acceptable_device_input
    url = f"https://public-api.apptweak.com/api/public/store/apps/metrics/history.json?apps={app}&metrics={metric}%2Cratings&start_date={beg_date}&end_date={end_date}&country={country_code}&device={device}"

    headers = {
        "accept": "application/json",
        "x-apptweak-key": "mEVu0O4Co6F1W1BcdGiofYHk4yo"
    }

    response = requests.get(url, headers=headers)

    return response.text

#Set variable answer to the output of defined function, pass in variable app = app_name, metric = metric_name
answer = request(app_name, metric_name, beginning_date, end_date, country_code, device)
print(answer)


