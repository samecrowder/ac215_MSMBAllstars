from io import StringIO
import logging
import os

from google.cloud import storage
import pandas as pd

from .helper import preprocess_data

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# GCS
BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "default-bucket-name")
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
DATA_FOLDER = os.environ.get("DATA_FOLDER")
DATA_FILE = os.environ.get("DATA_FILE")


logging.info(f"Using GCS bucket: {BUCKET_NAME}")
logging.info(f"Using GCS credentials: {GOOGLE_APPLICATION_CREDENTIALS}")

# Initialize GCS client
client = storage.Client()
bucket = client.bucket(BUCKET_NAME)
logging.info(f"Connected to GCS bucket: {BUCKET_NAME}")


def read_csv_from_gcs(bucket, file_name):
    logging.info(f"Reading file: {file_name}")
    blob = bucket.blob(file_name)
    content = blob.download_as_text()
    return pd.read_csv(StringIO(content))


# Read data file
df = read_csv_from_gcs(bucket, os.path.join(DATA_FOLDER, DATA_FILE))
logging.info(f"Data shape: {df.shape}")

# Create dataset
df["tourney_date"] = pd.to_datetime(df["tourney_date"], format="%Y%m%d")
player_dfs, feature_cols = preprocess_data(df)
logging.info("In-memory databse loaded successfully")
