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


def main():

    #Import required python libraries - done within the function according to airflow best practices
    from decouple import config
    import os

    #Import python file dependencies
    from app_metric_methods import AppMetrics
    from music_app_config import music_apps

    #Fetch API Key from local env
    API_KEY = config('KEY')

    #Master Parameters - To be updated as required
    beginning_date = '2021-01-01' # Hard Beginning Date for Full loads, Default Beginning Date for Delta Loads (countries with no watermark date)
    end_date = '2021-01-5'
    metric_type = 'downloads' # 'downloads', 'ranking', 'rating' only supports one metric specified at a time
    load_type = 'F' # 'F' for Full or 'D' for Delta

    # Main Loop

    try:
        for app_name, devices in music_apps.items(): 

            #Initialise App Metrics Class
            app_metrics = AppMetrics(app_name, API_KEY, beginning_date, end_date, metric_type)

            # Set loop counter to write a csv header on the first loop and then have no header on the second loop
            count = 0  
            wm_count = 0       
            country_list = app_metrics.load_countries()  
            for country in country_list:
                for device, code in devices.items():

                    #Lookup beginning date from watermark table if load type is delta
                    #Beginning date for delta will be 1 day after the previous pipeline was run
                    if load_type == 'D':
                        csv_path = os.path.join(os.path.dirname(os.getcwd()), "data", "output_files", "master_watermark", "combined_watermark.csv")
                        beginning_date = app_metrics.lookup_beginning_date(csv_path, country, device)
                    elif load_type =='F':
                        pass
                    else:
                        raise Exception('Invalid load type provided')

                    #api_response = app_metrics.request(code, beginning_date, country, device)
                
                    #print(api_response)

                    #below api response commented out as an example response to use for testing
                    api_response = {"result":{"com.spotify.music":{"downloads":[{"value":151880,"date":"2021-01-01","precision":0.25},{"value":143522,"date":"2021-01-02","precision":0.25},{"value":117403,"date":"2021-01-03","precision":0.25},{"value":101042,"date":"2021-01-04","precision":0.25},{"value":89371,"date":"2021-01-05","precision":0.25}]}},"metadata":{"request":{"path":"/api/public/store/apps/metrics/history.json","params":{"device":"android","country":"in","language":"in","start_date":"2021-01-01","end_date":"2021-01-05","apps":["com.spotify.music"],"metrics":["downloads"]},"cost":701,"max_credit_cost":701,"status":200},"response":None}}
                    
                    #Extract downloads from request output
                    output_df = app_metrics.extract_metric_to_df(api_response)
                
                    # Add additional columns for context
                    output_df = app_metrics.add_dim_cols(api_response, output_df, ['device', 'country', 'language'])
                    print(output_df)

                    #Write output to CSV
                    app_metrics.csv_write(output_df, count, beginning_date)
                    count += 1
                    break
                break
            #Get Watermark for each app
            app_metrics.create_watermark(beginning_date)

            #Combine all Watermark files together
            app_metrics.combine_watermark(wm_count)
            wm_count += 1
            break
       

        return True

    except Exception as e:
        raise e


if __name__ == "__main__":
    main()
    



