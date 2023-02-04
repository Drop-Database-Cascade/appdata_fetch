#This file contains the class and methods required to create dim tables locally.
import csv
import os
import datetime

#Import Parent Class
from local_file_operations_class import local_file_operations


class dim_table_local_file_operations(local_file_operations):

    def __init__(self):
        local_file_operations.__init__(self)
        self.dim_path = os.path.join(self.output_path, 'dim_tables')

    #Create a two column country csv dim table with an index based on a lookup dictionary of Country Codes:Country Names
    def write_dim_country_to_csv(self, country_codes:dict, file_name:str):
        with open(os.path.join(self.dim_path, file_name), mode='w') as csv_file:
            fieldnames = ['index', 'code', 'name']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames, lineterminator= '\n')
            writer.writeheader()
            for index, (code, name) in enumerate(country_codes.items(), 1):
                writer.writerow({'index': index, 'code': code, 'name': name})
            return True
        
    def get_date_int(self, date_string):
        year, month, day = map(int, date_string.split("-"))
        return year, month, day
        
    #Write a dimension date column to a csv
    def write_dates_to_csv(self, file_name:str, end_year:int,end_month:int, end_day:int):
        with open(os.path.join(self.dim_path, file_name), mode='w') as csv_file:
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