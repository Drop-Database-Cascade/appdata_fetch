import csv
from pathlib import Path
from country_codes_config import country_codes

'''This code writes a CSV file (Country Dimension) containing a list of country codes and their corresponding country names. 
The country codes are matched to the full country name in the country_codes dictionary.'''


def write_country_codes_to_csv_with_index(country_codes, file_name):
    with open(file_name, mode='w') as csv_file:
        fieldnames = ['index', 'code', 'name']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, lineterminator= '\n')
        writer.writeheader()
        for index, (code, name) in enumerate(country_codes.items(), 1):
            writer.writerow({'index': index, 'code': code, 'name': name})
        return True

def main():
    dim_country_output = Path.cwd() / 'output_files' / 'dim_tables' / 'dim_country.csv'
    # Create the data directory if it doesn't exist
    dim_country_output.parent.mkdir(exist_ok=True, parents=True)
    write_country_codes_to_csv_with_index(country_codes, dim_country_output)
    return True

if __name__ == "__main__":
    main()
