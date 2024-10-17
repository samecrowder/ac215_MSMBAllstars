import os
import logging
from google.cloud import storage
import pandas as pd
from io import StringIO

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# GCS
BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "default-bucket-name")
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
RAW_DATA_FOLDER = "raw_data"

logging.info(f"Using GCS bucket: {BUCKET_NAME}")
logging.info(f"Using GCS credentials: {GOOGLE_APPLICATION_CREDENTIALS}")


def list_csv_files(bucket, prefix):
    logging.info(f"Listing CSV files in {prefix}")
    files = [
        blob.name
        for blob in bucket.list_blobs(prefix=prefix)
        if blob.name.endswith(".csv")
    ]
    logging.info(f"Found {len(files)} CSV files")
    return files


def read_csv_from_gcs(bucket, file_name):
    logging.info(f"Reading file: {file_name}")
    blob = bucket.blob(file_name)
    content = blob.download_as_text()
    return pd.read_csv(StringIO(content))


def get_next_version(bucket):
    logging.info("Determining next version number")
    versions = [
        blob.name.split("/")[0]
        for blob in bucket.list_blobs()
        if blob.name.startswith("version")
    ]
    if not versions:
        return "version1"
    latest_version = max(versions, key=lambda x: int(x[7:]))
    next_version = f"version{int(latest_version[7:]) + 1}"
    logging.info(f"Next version will be: {next_version}")
    return next_version


def main():
    logging.info("Starting preprocessing script")

    # Initialize GCS client
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    logging.info(f"Connected to GCS bucket: {BUCKET_NAME}")

    # List all CSV files in the raw_data folder
    csv_files = list_csv_files(bucket, RAW_DATA_FOLDER)

    # Read and concatenate all CSV files
    logging.info("Reading and concatenating CSV files")
    all_data = pd.concat([read_csv_from_gcs(bucket, file) for file in csv_files])
    logging.info(f"Combined data shape: {all_data.shape}")

    # Determine the next version folder
    next_version = get_next_version(bucket)

    # Write the combined data to a new CSV in the next version folder
    output_file = f"{next_version}/combined_atp_matches.csv"
    logging.info(f"Writing combined data to {output_file}")
    bucket.blob(output_file).upload_from_string(
        all_data.to_csv(index=False), "text/csv"
    )

    logging.info(f"Combined data successfully written to {output_file}")
    logging.info("Preprocessing completed")


if __name__ == "__main__":
    main()
