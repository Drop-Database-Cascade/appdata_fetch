#This file tests the app_metrics request class (app_metric_classes.py) using the pytest library to conduct unit tests

import pytest
import requests
import pandas as pd
import os, sys
import datetime


sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'etl_scripts')))

# Import the class to be tested
from app_metric_classes import app_metrics_requests

# Define a fixture to provide data for testing
@pytest.fixture
def metric_data():
    return {
        'result': {
            'com.example.app': {
                'downloads': [
                    {'date': '2021-01-01', 'value': 100, 'precision': 'day'},
                    {'date': '2021-01-02', 'value': 200, 'precision': 'day'},
                ]
            }
        },
        'metadata': {
            'request': {
                'params': {
                    'device': 'android',
                    'country': 'US',
                }
            }
        }
    }

# Test the request method
def test_request(monkeypatch):
    # Monkeypatch the requests.get method to return a mock response
    def mock_response(*args, **kwargs):
        class MockResponse:
            def __init__(self):
                self.json_data = {'key': 'value'}

            def json(self):
                return self.json_data

        return MockResponse()

    monkeypatch.setattr(requests, 'get', mock_response)

    # Create an instance of the class
    app_metrics = app_metrics_requests(
        app_name='spotify', 
        beginning_date='2021-01-01', 
        end_date='2021-01-02', 
        metric_name='downloads'
    )

    # Send the request and check the response
    response = app_metrics.request(
        app='com.example.app',
        beg_date='2021-01-01',
        country='US',
        device='android'
    )
    assert response == {'key': 'value'}

# Test the extract_metric_to_df method
def test_extract_metric_to_df(metric_data):
    # Create an instance of the class
    app_metrics = app_metrics_requests(
        app_name='app_name', 
        beginning_date='2021-01-01', 
        end_date='2021-01-02', 
        metric_name='downloads'
    )

    # Extract the metric data to a DataFrame
    df = app_metrics.extract_metric_to_df(metric_data)

    # Check the data in the DataFrame
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)
    assert df.columns.tolist() == ['date', 'downloads']
    assert df.iloc[0].tolist() == ['2021-01-01', 100]

def test_add_dim_cols():
    # Initialize the class
    app_metrics = app_metrics_requests(
        app_name='app_1', 
        beginning_date='2022-01-01', 
        end_date='2022-01-03', 
        metric_name='downloads'
    )
    
    # Create sample data
    json_dict = {'result': {'app_1': {'device': 'mobile', 'country': 'US', 'language': 'en'}}, 
                 'metadata': {'request': {'params': {'device': 'mobile', 'country': 'US', 'language': 'en'}}}}
    df = pd.DataFrame({'date': ['2022-01-01', '2022-01-02', '2022-01-03']})
    cols = ['device', 'country', 'language']
    
    # Call the add_dim_cols method
    result_df = app_metrics.add_dim_cols(json_dict, df, cols)
    
    # Check if the correct columns have been added
    assert 'apps' in result_df.columns
    assert 'device' in result_df.columns
    assert 'country' in result_df.columns
    assert 'language' in result_df.columns
    assert 'date_key' in result_df.columns
    assert 'app_name' in result_df.columns
    
    # Check if the values in the columns are correct
    assert result_df['apps'].values[0] == 'app_1'
    assert result_df['device'].values[0] == 'mobile'
    assert result_df['country'].values[0] == 'US'
    assert result_df['language'].values[0] == 'en'
    assert result_df['date_key'].values[0] == 20220101
    assert result_df['app_name'].values[0] == app_metrics.app_name

def test_calculate_total_credit_cost():
    # Initialize the class
    app_metrics = app_metrics_requests(
        app_name='spotify', 
        beginning_date='2022-01-01', 
        end_date='2022-01-03', 
        metric_name='downloads'
    )
    
    # Create sample data
    matrix = {'App Metrics': {'downloads': {'base_credit_cost': 100, 'extra_credit_cost_per_day': 10}}}
    beginning_date = '2022-01-01'
    
    # Call the calculate_total_credit_cost method
    result = app_metrics.calculate_total_credit_cost(matrix, beginning_date)
    
    # Check if the result is correct
    assert result == 120

def test_check_cost_budget():
    # Initialize the class
    app_metrics = app_metrics_requests(
        app_name='spotify', 
        beginning_date='2021-01-01', 
        end_date='2021-01-02', 
        metric_name='downloads'
    )
    
    # Test for success scenario
    budget = 200
    total_cost = 100
    result = app_metrics.check_cost_budget(budget, total_cost)
    assert result == True
    
    # Test for failure scenario
    budget = 50
    total_cost = 100
    with pytest.raises(ValueError) as exception_info:
        app_metrics.check_cost_budget(budget, total_cost)
