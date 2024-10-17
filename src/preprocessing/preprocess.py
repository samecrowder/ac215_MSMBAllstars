import os
from google.cloud import storage
import pandas as pd
from io import StringIO

IMG_SIZE = 128

# GCS
BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "default-bucket-name")
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

# Constants
RAW_DATA_FOLDER = "raw_data"
FILE_PREFIX = "atp_matches_"


def list_csv_files(bucket, prefix):
    return [
        blob.name
        for blob in bucket.list_blobs(prefix=prefix)
        if blob.name.endswith(".csv")
    ]


def read_csv_from_gcs(bucket, file_name):
    blob = bucket.blob(file_name)
    content = blob.download_as_text()
    return pd.read_csv(StringIO(content))


def get_next_version(bucket):
    versions = [
        blob.name.split("/")[0]
        for blob in bucket.list_blobs()
        if blob.name.startswith("version")
    ]
    if not versions:
        return "version1"
    latest_version = max(versions, key=lambda x: int(x[7:]))
    return f"version{int(latest_version[7:]) + 1}"


def main():
    # Initialize GCS client
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    # List all CSV files in the raw_data folder
    csv_files = list_csv_files(bucket, RAW_DATA_FOLDER)

    # Read and concatenate all CSV files
    all_data = pd.concat([read_csv_from_gcs(bucket, file) for file in csv_files])

    # Determine the next version folder
    next_version = get_next_version(bucket)

    # Write the combined data to a new CSV in the next version folder
    output_file = f"{next_version}/combined_atp_matches.csv"
    bucket.blob(output_file).upload_from_string(
        all_data.to_csv(index=False), "text/csv"
    )

    print(f"Combined data written to {output_file}")


if __name__ == "__main__":
    main()
