import pytest
from unittest.mock import patch, MagicMock
from utils.bq_ops import BQOps
import json

@pytest.fixture
def mock_bq_client():
    with patch('google.cloud.bigquery.Client') as mock:
        yield mock

@pytest.fixture
def mock_get_place_id():
    with patch('utils.bq_ops.get_place_id') as mock:
        mock.return_value = "test_place_id"
        yield mock

def test_format_json_for_bq(mock_bq_client, mock_get_place_id):
    # Initialize BQOps
    ops = BQOps()
    
    # Sample input JSON (string)
    sample_json = """```json
    {
        "events": [
            {
                "name": "Test Event",
                "description": "A test event",
                "location": "Seattle",
                "start_date": "2025-07-15",
                "end_date": "2025-07-20",
                "url": "http://test.com",
                "category": "test"
            }
        ]
    }
    ```"""
    
    # Run the formatting logic
    result = ops.format_json_for_bq(sample_json)
    
    # Verify results
    assert "events" in result
    assert len(result["events"]) == 1
    event = result["events"][0]
    assert event["unique_id"] == "test_place_id_2025-07-15_2025-07-20"
    assert event["name"] == "Test Event"

def test_insert_to_bq_logic(mock_bq_client, mock_get_place_id):
    # Setup mock client behavior
    mock_instance = mock_bq_client.return_value
    mock_instance.insert_rows_json.return_value = [] # No errors
    
    ops = BQOps()
    
    sample_json = """{
        "events": [
            {
                "name": "Test Event",
                "description": "A test event",
                "location": "Seattle",
                "start_date": "2025-07-15",
                "end_date": "2025-07-20",
                "url": "http://test.com",
                "category": "test"
            }
        ]
    }"""
    
    with patch.dict('os.environ', {'EVENTS_DATA_TABLE': 'project.dataset.table'}):
        ops.insert_to_bq(sample_json, "SEA")
    
    # Check if insert_rows_json was called with correct data
    args, kwargs = mock_instance.insert_rows_json.call_args
    assert args[0] == 'project.dataset.table'
    assert len(args[1]) == 1
    assert args[1][0]['destination'] == "SEA"
    assert args[1][0]['id'] == "test_place_id_2025-07-15_2025-07-20"


def test_get_events_logic(mock_bq_client):
    # Setup mock client behavior
    mock_instance = mock_bq_client.return_value
    mock_query_job = MagicMock()
    
    # Mock row returned from BigQuery
    mock_row = {
        "name": "Test Event",
        "description": "A test",
        "destination": "SEA",
        "start_date": "2025-07-15",
        "timestamp": None
    }
    mock_query_job.result.return_value = [mock_row]
    mock_instance.query.return_value = mock_query_job
    
    ops = BQOps()
    
    with patch.dict('os.environ', {'EVENTS_DATA_TABLE': 'test_table'}):
        results = ops.get_events(destination="SEA", start_date="2025-07-15", end_date="2025-07-31")
    
    # Check results
    assert len(results) == 1
    assert results[0]['name'] == "Test Event"
    
    # Check if query was called with correct parameters
    args, kwargs = mock_instance.query.call_args
    assert "SELECT * FROM `test_table`" in args[0]
    
    # Check job config
    job_config = kwargs['job_config']
    query_params = job_config.query_parameters
    
    assert len(query_params) == 3
    param_names = [p.name for p in query_params]
    assert "destination" in param_names
    assert "start_date" in param_names
    assert "end_date" in param_names
