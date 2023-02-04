#This file tests the local_file_operations_class.py methods using the pytest library to conduct unit tests

import os, sys
import shutil
import csv
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'etl_scripts')))
from local_file_operations_class import local_file_operations

test_input_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "input_files", "test")
test_output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "output_files", "test")

@pytest.fixture
def cleanup_files():
    # cleanup code to remove any files written by the tests
    os.makedirs(test_output_dir, exist_ok = True)
    os.makedirs(test_input_dir, exist_ok = True)
    yield
    # cleanup code to remove the temporary test directory
    shutil.rmtree(test_output_dir)
    shutil.rmtree(test_input_dir)

class TestFilesOperationsClass:

    def test_write_blank_csv(self, cleanup_files):
        lfo = local_file_operations()
        assert lfo.write_blank_csv("test/test_write_blank_csv.csv", ["col1", "col2", "col3"]) == True
        
    def test_dict_append_line_csv(self, cleanup_files):
        lfo = local_file_operations()
        lfo.write_blank_csv("test/test_dict_append_line_csv.csv", ["col1", "col2", "col3"])
        assert lfo.dict_append_line_csv("test/test_dict_append_line_csv.csv", {"col1": "value1", "col2": "value2", "col3": "value3"}) == True

    def test_insert_line_below_header_csv(self, cleanup_files):
        lfo = local_file_operations()
        lfo.write_blank_csv("test/test_insert_line_below_header_csv.csv", ["col1", "col2", "col3"])
        lfo.insert_line_below_header_csv("test/test_insert_line_below_header_csv.csv", ["value1", "value2", "value3"])
        
    def test_load_csv_to_list(self, cleanup_files):
        lfo = local_file_operations()
        with open(f"{test_input_dir}/test_load_csv_to_list.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerows([["value1"], ["value2"], ["value3"]])
        assert lfo.load_csv_to_list("test/test_load_csv_to_list.csv") == ["value2", "value3"]