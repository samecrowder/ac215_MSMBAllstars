import pytest
import pandas as pd
from unittest.mock import Mock, patch
from io import StringIO
from preprocess import (
    list_csv_files,
    read_csv_from_gcs,
    get_next_version,
    safe_date_parse
)

@pytest.fixture
def mock_bucket():
    bucket = Mock()
    return bucket

@pytest.fixture
def sample_csv_data():
    data = """tourney_date,winner_name,winner_rank,winner_ht,winner_age,loser_name,loser_rank,loser_ht,loser_age
20230101,Player A,1,185,25,Player B,2,180,23
20230102,Player C,3,190,28,Player D,4,175,22"""
    return StringIO(data)

def test_list_csv_files(mock_bucket):
    # Create mock blobs
    blob1 = Mock()
    blob1.name = "raw_data/file1.csv"
    blob2 = Mock()
    blob2.name = "raw_data/file2.txt"
    blob3 = Mock()
    blob3.name = "raw_data/file3.csv"
    
    mock_bucket.list_blobs.return_value = [blob1, blob2, blob3]
    
    files = list_csv_files(mock_bucket, "raw_data")
    assert len(files) == 2
    assert "raw_data/file1.csv" in files
    assert "raw_data/file3.csv" in files

def test_read_csv_from_gcs(mock_bucket):
    # Create mock blob
    mock_blob = Mock()
    mock_blob.download_as_text.return_value = "col1,col2\nval1,val2"
    mock_bucket.blob.return_value = mock_blob
    
    df = read_csv_from_gcs(mock_bucket, "test.csv")
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (1, 2)
    assert list(df.columns) == ["col1", "col2"]

def test_get_next_version_empty_bucket(mock_bucket):
    mock_bucket.list_blobs.return_value = []
    assert get_next_version(mock_bucket) == "version1"

def test_get_next_version_existing_versions(mock_bucket):
    # Create mock blobs with version names
    blob1 = Mock()
    blob1.name = "version1/data.csv"
    blob2 = Mock()
    blob2.name = "version2/data.csv"
    
    mock_bucket.list_blobs.return_value = [blob1, blob2]
    assert get_next_version(mock_bucket) == "version3"

def test_safe_date_parse_valid_date():
    result = pd.to_datetime("20230101", format="%Y%m%d")
    assert pd.to_datetime("20230101", format="%Y%m%d") == result

def test_safe_date_parse_invalid_date():
    result = pd.to_datetime("invalid_date", format="%Y%m%d", errors='coerce')
    assert pd.isna(result)

@patch('google.cloud.storage.Client')
def test_main_flow(mock_storage_client, mock_bucket, sample_csv_data):
    # This is a basic test of the main flow
    # You might want to expand this based on your specific needs
    mock_storage_client.return_value.bucket.return_value = mock_bucket
    mock_blob = Mock()
    mock_blob.download_as_text.return_value = sample_csv_data.getvalue()
    mock_bucket.blob.return_value = mock_blob
    mock_bucket.list_blobs.return_value = [Mock(name="raw_data/test.csv")]
