#This file tests the dim_table_class.py methods using the pytest library to conduct unit tests

import pytest
import os, sys
import csv
import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'etl_scripts')))
from dim_table_class import dim_table_local_file_operations

#Class Init
dim_test = dim_table_local_file_operations()

def test_write_dim_country_to_csv(tmpdir):
    dim_table = dim_table_local_file_operations()
    dim_table.output_path = tmpdir.strpath
    country_codes = {'US': 'United States', 'UK': 'United Kingdom'}
    file_name = 'dim_country_test.csv'
    assert dim_table.write_dim_country_to_csv(country_codes, file_name) == True
    csv_file = os.path.join(dim_table.dim_path, file_name)
    assert os.path.exists(csv_file) == True
    with open(csv_file, 'r') as f:
        contents = f.read()
        print(contents)
        assert "US", "United States" in contents
        assert "UK", "United Kingdom" in contents

def test_get_date_int():
    dim_table = dim_table_local_file_operations()
    date_string = '2022-01-01'
    assert dim_table.get_date_int(date_string) == (2022, 1, 1)

def test_write_dates_to_csv():
    end_year, end_month, end_day = 2022, 2, 1
    file_name = "test_dates.csv"
    obj = dim_table_local_file_operations()
    result = obj.write_dates_to_csv(file_name, end_year, end_month, end_day)

    assert result == True
    file_path = os.path.join(obj.dim_path, file_name)
    with open(file_path, "r") as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader]
    
    start_date = datetime.datetime(2010, 1, 1)
    end_date = datetime.datetime(end_year, end_month, end_day)
    expected_rows = (end_date - start_date).days + 1
    assert len(rows) == expected_rows

# Clean up the output files after tests are done
def teardown_module(module):
    os.remove(os.path.join(dim_test.dim_path, 'dim_country_test.csv'))
    os.remove(os.path.join(dim_test.dim_path, 'test_dates.csv'))


