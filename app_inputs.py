#Define dictionary of possible combinations
music_apps = {
    "spotify": {
        "android": "com.spotify.tv.android",
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
    }
}

for app_name, devices in music_apps.items():
    #Get App Country List function
    country_list = load_countries(app_name)
    for country in country_list:
        for device, code in devices.items():
            api_response = request(code, metric_type, beginning_date, end_date, country, device,API_KEY)
            print(code)