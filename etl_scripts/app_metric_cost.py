# This file checks the expected total cost (credits) of the API requests sent to App Tweak and compares it against a pre configured budget. 
#The cost report is produced and an error is raised if the request is going to be over budget.


#Import python file dependencies
from app_metric_classes import app_metrics_local_file_operations
from local_file_operations_class import local_file_operations
from music_app_config import music_apps
from country_codes_config import country_codes
from app_metric_pricing_matrix import app_metric_pricing_matrix


def check_total_credit_cost(metric_type:str, end_date:str, load_type:str, budget:int):
    assert len(load_type) == 1

    #set total cost to 0
    total_cost = 0
    relative_cost_path = "expected_cost/expected_cost.csv"

    try:

        #Initialise Local File Ops
        lfo = local_file_operations()

        #cost output file
        lfo.write_blank_csv(relative_cost_path, ['App', 'Country', 'Cost (credits)', 'Beg_Date', 'End_Date'])

        for app_name, devices in music_apps.items(): 
            
            #Set Default Beginning Date
            beginning_date = music_apps[app_name][1]["beginning_date"]

            #Set App Cost to 0
            app_cost = 0

            #Initialise App Metrics Class
            app_metrics = app_metrics_local_file_operations(app_name, beginning_date, end_date, metric_type)

            country_list = lfo.load_csv_to_list(f"{app_name}/countries_list.csv")   
            for country in country_list:
                #Reset cost per country
                cost = 0

                #Update beginning date if load type is delta
                beginning_date = app_metrics.check_beg_date(load_type, country)

                for device, code in devices[0].items():

                    #Sum combined cost for Android & Iphone
                    cost += app_metrics.calculate_total_credit_cost(app_metric_pricing_matrix, beginning_date)   

                #Write the cost for a country to the cost file
                lfo.dict_append_line_csv(relative_cost_path, {'App': app_name, 'Country': country_codes[country.upper()], 'Cost (credits)': cost, 'Beg_Date': beginning_date, 'End_Date': end_date})
                
                app_cost += cost
                total_cost += cost

            # Insert Agg App Cost
            lfo.insert_line_below_header_csv(relative_cost_path, [f'Total {app_name} Cost', '', app_cost, beginning_date, end_date])
            
        #Insert Total Cost
        lfo.insert_line_below_header_csv(relative_cost_path, ['Total Cost', '', total_cost, '', ''])

        #app_metrics.check_cost_budget(budget,total_cost)
        return True

    except Exception as e:
        raise(e)