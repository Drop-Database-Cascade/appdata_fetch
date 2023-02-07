#-----------------------------------------DESCRIPTION-----------------------------------------#
# This script will loop though the music apps dictionary and conduct the following actions
# 1.    Fetch app_tweak API Key stored in the local environment file
# 2.    Load in music_apps json object file. This contains the list of each source app to retrieve data about, the sub devices (iphone or android) and the corresponding api code.
# 3.    Load in user defined parameters (beginning date, end date, metric type, data load/extraction type)
# 4.    Loop through the different music streaming services in the Json object
# 5.    Load in a list of countries for to iterate through for each source app (significant regions the app is operating in). Located at data/input_files/{app_name}/countries_list.csv
# 6.    For each country, iterate through sub devices (Android & Iphone)
# 7.    If load type is Delta, the beginning date for each country is determined by the most recent data load end date, otherwise the user provided end date is used
# 8.    A request is sent to app_tweak api to receive a response in Json format for desired metric data
# 9.    JSON response is transformed to a Pandas dataframe with additional context columns added
# 10.   Dataframe is written to Csv file at data/output_files/{app_name}/countries_list.csv
# 11.   Watermark file is created both for individual apps and a combined aggregate located at data/output_files/master_watermark


#Import python file dependencies
from app_metric_classes import app_metrics_local_file_operations
from local_file_operations_class import local_file_operations
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '/data/input_files/')))
from music_app_config import music_apps


def app_metrics_fetch(metric_type:str, load_type:str, end_date:str):
    assert len(load_type) == 1

    # Main Loop
    try:
        for app_name, devices in music_apps.items(): 

            #Set Default Beginning Date
            beginning_date = music_apps[app_name][1]["beginning_date"]
            
            #Initialise App Metrics File Operations Class
            app_metric = app_metrics_local_file_operations(app_name, beginning_date, end_date, metric_type)

            #Initialise Local File Ops Class
            lfo = local_file_operations()

            # Set loop counter to write a csv header on the first loop and then have no header on the second loop
            count = 0  
            wm_count = 0       
            country_list = lfo.load_csv_to_list(f"{app_name}/countries_list.csv")  
            for country in country_list:

                #overwrite beginning date from watermark table if load type is delta
                beginning_date = app_metric.check_beg_date(load_type, country)

                for device, code in devices[0].items():

                    #api_response = app_by_country.request(code, beginning_date, country, device)
                    #print(api_response)

                    #below api response commented out as an example response to use for testing
                    api_response = {"result":{"com.spotify.music":{"downloads":[{"value":151880,"date":"2021-01-01","precision":0.25},{"value":143522,"date":"2021-01-02","precision":0.25},{"value":117403,"date":"2021-01-03","precision":0.25},{"value":101042,"date":"2021-01-04","precision":0.25},{"value":89371,"date":"2021-01-05","precision":0.25}]}},"metadata":{"request":{"path":"/api/public/store/apps/metrics/history.json","params":{"device":"android","country":"in","language":"in","start_date":"2021-01-01","end_date":"2021-01-05","apps":["com.spotify.music"],"metrics":["downloads"]},"cost":701,"max_credit_cost":701,"status":200},"response":None}}
                    
                    #Extract downloads from request output
                    output_df = app_metric.extract_metric_to_df(api_response)
                
                    # Add additional columns for context
                    output_df = app_metric.add_dim_cols(api_response, output_df, ['device', 'country', 'language'])
                    print(output_df)

                    #Write output to CSV
                    app_metric.csv_write(output_df, count)
                    count += 1
                    break
                break
            #Get Watermark for each app
            app_metric.create_watermark()

            #Combine all Watermark files together
            app_metric.combine_watermark(wm_count)
            wm_count += 1
            break
       
        return True

    except Exception as e:
        raise e

def main():
    #Main function created to run script optionally without Airflow

    end_date = '2021-01-05'
    metric_type = 'downloads' # 'downloads', 'ranking', 'rating' only supports one metric specified at a time
    load_type = 'F' # 'F' for Full or 'D' for Delta
    app_metrics_fetch(metric_type, load_type, end_date)
    return True

if __name__ == "__main__":
    main()
    



