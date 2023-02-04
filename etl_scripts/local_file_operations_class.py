#This file contains the local_file_operations class
import csv
import os
from decouple import Config, RepositoryEnv

class local_file_operations:
# Fetches project root directory from the config file. Contains methods to interact with the local file system. All methods are currently csv based.

    def __init__(self):
        
        #Fetch Project Root from local env
        curfile_dir = os.path.dirname(os.path.abspath(__file__))
        env_file = os.path.join(os.path.dirname(curfile_dir), ".env")
        self.config = Config(RepositoryEnv(env_file))

        #Def Parent variables
        self.PROJECT_ROOT_PATH = self.config("PROJECT_ROOT_PATH")
        self.output_path = os.path.join(self.PROJECT_ROOT_PATH, "data", "output_files")
        self.input_path = os.path.join(self.PROJECT_ROOT_PATH, "data", "input_files")     

    #Create a blank csv with headers
    def write_blank_csv(self, relative_path:str, fieldnames:list):
        with open(os.path.join(self.output_path, relative_path), 'w', newline='') as csvfile:
            fieldnames =  fieldnames   #['App', 'Country', 'Cost']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
        return True
    
    # Add row to CSV based on header:value pair
    def dict_append_line_csv(self, relative_path:str, records:dict):
        headers = list(records.keys())
        with open(os.path.join(self.output_path, relative_path), 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writerow(records)
        return True
    
    #Insert row into csv directly below the header
    def insert_line_below_header_csv(self, relative_path:str, insert_list:list):
        with open(os.path.join(self.output_path, relative_path), 'r') as csvfile:
            data = list(csv.reader(csvfile))
        data.insert(1, insert_list)  #['Total Cost', '', total_cost]
        with open(os.path.join(self.output_path, relative_path), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(data)
    
    #Load CSV to List
    def load_csv_to_list(self, relative_path:str):
        #load countries into a list based on input config file
        output_list = []

        with open(os.path.join(self.input_path, relative_path), "r") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                output_list.append(row[0])
        return output_list

