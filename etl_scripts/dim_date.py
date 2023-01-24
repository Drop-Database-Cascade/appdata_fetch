import datetime
import csv
from pathlib import Path

''' This creates a date dimension table as a csv which contains daily dates between 1 Jan 2010 and an end date passed as a parameter. The columns produced are Index, date_key, date, 
year, month(int), day, month(str). file name is the path to csv location'''

def write_dates_to_csv(file_name, end_year=int,end_month=int, end_day=int):
    with open(file_name, mode='w') as csv_file:
        fieldnames = ['index', 'date_key', 'date','day','month','year','month_string']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, lineterminator= '\n')
        writer.writeheader()
        start_date = datetime.datetime(2010, 1, 1)
        end_date = datetime.datetime(end_year, end_month, end_day )
        current_date = start_date
        index = 1
        while current_date <= end_date:
            date_key = current_date.strftime('%Y%m%d')
            month_string = current_date.strftime('%B')
            writer.writerow({'index': index, 'date_key': date_key, 'date': current_date.strftime('%Y-%m-%d'),'day':current_date.day,'month':current_date.month,'year':current_date.year,'month_string':month_string})
            current_date += datetime.timedelta(days=1)
            index += 1
    return True


def main():
    dim_date_output = Path.cwd() / 'output_files' / 'dim_tables' / 'dim_date.csv'
    # Create the data directory if it doesn't exist
    dim_date_output.parent.mkdir(exist_ok=True, parents=True)
    write_dates_to_csv(dim_date_output, 2022,12,31)
    return True

if __name__ == "__main__":
    main()