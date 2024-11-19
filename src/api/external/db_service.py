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

# GCS config constants
BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "msmballstars-data")
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
DATA_FOLDER = os.environ.get("DATA_FOLDER", "version1")
DATA_FILE = os.environ.get("DATA_FILE", "combined_atp_matches.csv")


def get_gcs_client():
    """Initialize and return GCS client"""
    if os.environ.get("ENV") == "test":
        return None

    client = storage.Client()
    return client


def read_csv_from_gcs(bucket, file_name):
    logging.info(f"Reading file: {file_name}")
    blob = bucket.blob(file_name)
    content = blob.download_as_text()
    return pd.read_csv(StringIO(content))


def load_data():
    """Load data from GCS and preprocess it."""
    if os.environ.get("ENV") == "test":
        return None, None

    client = get_gcs_client()
    bucket = client.bucket(BUCKET_NAME)

    df = read_csv_from_gcs(bucket, os.path.join(DATA_FOLDER, DATA_FILE))
    logging.info(f"Data shape: {df.shape}")

    # Create dataset
    df["tourney_date"] = pd.to_datetime(df["tourney_date"], format="mixed")
    player_dfs, feature_cols = preprocess_data(df)
    logging.info("In-memory database loaded successfully")

    return player_dfs, feature_cols
