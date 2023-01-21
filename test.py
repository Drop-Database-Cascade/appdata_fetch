import requests

url = "https://public-api.apptweak.com/api/public/store/apps/metrics/history.json?apps=com.spotify.tv.android&metrics=downloads%2Cratings&start_date=2022-01-01&end_date=2022-01-02&country=us&device=com.android"

headers = {
    "accept": "application/json",
    "x-apptweak-key": "APPTWEAK-API-KEY"
}

response = requests.get(url, headers=headers)

print(response.text)


