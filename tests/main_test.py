import gradio as gr
from bson.objectid import ObjectId
from datetime import datetime

import pytest
import main
import unittest.mock as mock

def test_date_format():
    # Test with date format '%m/%d/%y'
    assert main.date_format('12/31/20') == datetime.strptime('12/31/20', '%m/%d/%y')

    # Test with date format '%m/%d/%Y'
    assert main.date_format('12/31/2020') == datetime.strptime('12/31/2020', '%m/%d/%Y')

    # Test with date format '%m%d%Y'
    assert main.date_format('12312020') == datetime.strptime('12312020', '%m%d%Y')

    # Test with invalid date format
    with pytest.raises(gr.Error):
        main.date_format('2020-12-31')

@mock.patch("pymongo.collection.Collection.find_one")
def test_authenticate(mock_find_one):
    mock_find_one.return_value = {"username": "test", "password": "", "role": "administrator"}
    session_state = {}
    result = main.authenticate("test", session_state)
    print(result)
    assert result == ("Login successful", {"user": "test"})

@mock.patch("pymongo.collection.Collection.find")
def test_get_patients(mock_find):
    expected_result = [("Doe" + ", " + "John" + " (" + '01/01/2000' + ")", '6599236adf19d0f8ee32b2d1')]
    mock_find.return_value = [{"_id": ObjectId('6599236adf19d0f8ee32b2d1'), "last_name": "Doe", "first_name": "John", "dob": datetime.strptime('01/01/2000', '%m/%d/%Y')}]
    assert main.get_patients() == expected_result

@mock.patch("pymongo.collection.Collection.find_one")
@mock.patch("pymongo.collection.Collection.insert_one")
def test_set_patient(mock_insert_one, mock_find_one):
    pass

@mock.patch("pymongo.collection.Collection.find")
def test_list_denials(mock_find):
    pass

@mock.patch("pymongo.collection.Collection.find_one_and_update")
@mock.patch("pymongo.collection.Collection.insert_one")
def test_set_denial(mock_insert_one, mock_find_one_and_update):
    pass

def test_gather_report_state():
    assert main.gather_report_state("filter", "filter_condition", "value", "sort", "sort_condition") == {"filter": "filter", "filter_condition": "filter_condition", "filter_value": "value", "sort": "sort", "sort_condition": "sort_condition"}