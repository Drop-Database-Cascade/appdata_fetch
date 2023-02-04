from country_codes_config import country_codes
from dim_table_class import dim_table_local_file_operations

#This code writes a CSV file (Country Dimension) containing a list of country codes and their corresponding country names. 
#The country codes are matched to the full country name in the country_codes dictionary.

def main():

    #Main Function
    try:
        dim = dim_table_local_file_operations()
        dim.write_dim_country_to_csv(country_codes, "dim_country.csv")
        return True
    except Exception as e:
        raise(e)

if __name__ == "__main__":
    main()
