#!/bin/bash

# Check if the "data" folder in app_data_fetch_app is empty
if [ "$(ls -A appdata_fetch_app/data)" ]; then
  echo "appdata_fetch_app/data is not empty, cannot replace."
  exit 1
else

  # Copy the "data" folder in initdata_files_appdata_fetch_app to app_data_fetch_app
  cp -r initdata_files_appdata_fetch_app/data appdata_fetch_app
  exit 1
fi;