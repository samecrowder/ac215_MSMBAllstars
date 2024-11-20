import pytest
import pandas as pd
import sys
import os
from io import StringIO
from google.cloud import storage

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from preprocess import (
    list_csv_files,
    read_csv_from_gcs,
    get_next_version,
    safe_date_parse
)

@pytest.fixture
def mock_bucket():
    class MockBlob:
        def __init__(self, name, content=None):
            self.name = name
            self.content = content
            
        def download_as_text(self):
            return self.content
            
    class MockBucket:
        def __init__(self):
            self.blobs = []
            
        def list_blobs(self, prefix=None):
            if prefix:
                return [b for b in self.blobs if b.name.startswith(prefix)]
            return self.blobs
            
        def blob(self, name):
            for blob in self.blobs:
                if blob.name == name:
                    return blob
            return None
            
        def add_blob(self, name, content=None):
            self.blobs.append(MockBlob(name, content))
            
    return MockBucket()

def test_list_csv_files(mock_bucket):
    mock_bucket.add_blob("raw_data/file1.csv")
    mock_bucket.add_blob("raw_data/file2.txt")
    mock_bucket.add_blob("raw_data/file3.csv")
    
    files = list_csv_files(mock_bucket, "raw_data")
    assert len(files) == 2
    assert "raw_data/file1.csv" in files
    assert "raw_data/file3.csv" in files

def test_read_csv_from_gcs(mock_bucket):
    csv_content = "col1,col2\n1,2\n3,4"
    mock_bucket.add_blob("test.csv", csv_content)
    
    df = read_csv_from_gcs(mock_bucket, "test.csv")
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)
    assert list(df.columns) == ["col1", "col2"]

def test_get_next_version_empty_bucket(mock_bucket):
    version = get_next_version(mock_bucket)
    assert version == "version1"

def test_get_next_version_existing_versions(mock_bucket):
    mock_bucket.add_blob("version1/data.csv")
    mock_bucket.add_blob("version2/data.csv")
    
    version = get_next_version(mock_bucket)
    assert version == "version3"

def test_safe_date_parse():
    # Test valid date
    valid_date = "20230101"
    parsed_date = safe_date_parse(valid_date)
    assert not pd.isna(parsed_date)
    assert parsed_date.year == 2023
    assert parsed_date.month == 1
    assert parsed_date.day == 1
    
    # Test invalid date
    invalid_date = "invalid"
    parsed_date = safe_date_parse(invalid_date)
    assert pd.isna(parsed_date)
