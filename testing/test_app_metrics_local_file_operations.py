#This file tests the app_metrics_local_file_operations class (app_metric_classes.py) using the pytest library to conduct unit tests

import os, sys
import pandas as pd
import pytest
import shutil
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'etl_scripts')))

from app_metric_classes import app_metrics_local_file_operations

obj = app_metrics_local_file_operations("test", "2022-01-01", "2022-01-02", "downloads")
original_wm_file = obj.combined_watermark_path
temp_file = original_wm_file + ".tmp"


def test_csv_write():
    # initialize the object and create a sample DataFrame
    df = pd.DataFrame({
        'column_1': [1, 2, 3],
        'column_2': ['a', 'b', 'c']
    })
    
    # Create test directories if they don't exist
    os.makedirs(os.path.dirname(obj.app_data_csv_output), exist_ok=True)
    
    # test the first call to `csv_write`
    result = obj.csv_write(df, 0)
    assert result == True
    assert os.path.exists(obj.app_data_csv_output)
    
    # test the second call to `csv_write`
    result = obj.csv_write(df, 1)
    assert result == True

def test_create_watermark():
    # initialize the object and create a sample DataFrame
    df = pd.DataFrame({
        'app_name': ['app_name', 'app_name', 'app_name'],
        'country': ['country_1', 'country_2', 'country_3'],
        'device': ['device_1', 'device_2', 'device_3'],
        'date': ['2022-01-01', '2022-01-02', '2022-01-03']
    })
    df.to_csv(obj.app_data_csv_output, index=False)
    
    # Create test directories if they don't exist
    os.makedirs(os.path.dirname(obj.local_watermark_path), exist_ok=True)
    
    # test the `create_watermark` method
    result = obj.create_watermark()
    assert result == True
    assert os.path.exists(obj.local_watermark_path)
    
    # read the created watermark file and check the content
    df_watermark = pd.read_csv(obj.local_watermark_path)
    assert df_watermark.shape == (3, 4)
    assert df_watermark['date'].tolist() == ['2022-01-01', '2022-01-02', '2022-01-03']

def test_combine_watermark():
    # Untestable - without affecting production data
    pass
    
def test_lookup_beginning_date():
    
    # Move Existing Watermark File out of this folder
    shutil.copy(original_wm_file, temp_file)
    
    df = pd.DataFrame({
        "app_name": ["test"],
        "country": ["US"],
        "device": ["mobile"],
        "date": ["2022-01-01"]
    })

    df.to_csv(obj.combined_watermark_path, index=False)
    result = obj.lookup_beginning_date("US")
    assert result == "2022-01-02"

    # test case for a missing watermark
    result = obj.lookup_beginning_date("UK")
    assert result == "2022-01-01"

def test_check_beg_date():
    result = obj.check_beg_date("D", "US")
    assert result == "2022-01-02"

    result = obj.check_beg_date("F", "US")
    assert result == "2022-01-01"

    with pytest.raises(Exception) as e:
        obj.check_beg_date("invalid", "US")
    assert str(e.value) == "Invalid load type provided"

# Clean up the output files after tests are done
def teardown_module(module):
    os.remove(obj.app_data_csv_output)
    os.remove(obj.local_watermark_path)
    os.remove(obj.combined_watermark_path)

    #Move Combined Watermark Path Back
    shutil.copy(temp_file, original_wm_file)
    os.remove(temp_file)
    