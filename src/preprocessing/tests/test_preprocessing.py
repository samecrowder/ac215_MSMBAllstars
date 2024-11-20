from unittest.mock import Mock

import pandas as pd
from preprocess import get_next_version, list_csv_files, read_csv_from_gcs


def safe_date_parse(date_str):
    try:
        return pd.to_datetime(date_str, format="%Y%m%d")
    except ValueError:
        return pd.NaT


def test_list_csv_files():
    # Mock bucket and blobs
    mock_bucket = Mock()
    mock_blob1 = Mock()
    mock_blob1.name = "raw_data/file1.csv"
    mock_blob2 = Mock()
    mock_blob2.name = "raw_data/file2.txt"
    mock_blob3 = Mock()
    mock_blob3.name = "raw_data/file3.csv"

    mock_bucket.list_blobs.return_value = [mock_blob1, mock_blob2, mock_blob3]

    files = list_csv_files(mock_bucket, "raw_data")
    assert len(files) == 2
    assert "raw_data/file1.csv" in files
    assert "raw_data/file3.csv" in files


def test_read_csv_from_gcs():
    # Mock bucket and blob
    mock_bucket = Mock()
    mock_blob = Mock()
    mock_bucket.blob.return_value = mock_blob

    # Create sample CSV content
    csv_content = "col1,col2\n1,2\n3,4"
    mock_blob.download_as_text.return_value = csv_content

    df = read_csv_from_gcs(mock_bucket, "test.csv")
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)
    assert list(df.columns) == ["col1", "col2"]


def test_get_next_version_empty_bucket():
    # Mock empty bucket
    mock_bucket = Mock()
    mock_bucket.list_blobs.return_value = []

    version = get_next_version(mock_bucket)
    assert version == "version1"


def test_get_next_version_existing_versions():
    # Mock bucket with existing versions
    mock_bucket = Mock()
    mock_blob1 = Mock()
    mock_blob1.name = "version1/data.csv"
    mock_blob2 = Mock()
    mock_blob2.name = "version2/data.csv"

    mock_bucket.list_blobs.return_value = [mock_blob1, mock_blob2]

    version = get_next_version(mock_bucket)
    assert version == "version3"


def test_safe_date_parse():
    # Test valid date
    valid_date = "20230101"
    result = safe_date_parse(valid_date)
    assert pd.notna(result)
    assert result.strftime("%Y%m%d") == valid_date

    # Test invalid date
    invalid_date = "invalid"
    result = safe_date_parse(invalid_date)
    assert pd.isna(result)
