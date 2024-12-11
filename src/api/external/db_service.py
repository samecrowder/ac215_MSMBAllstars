from io import StringIO
import logging
import os

from google.cloud import storage
import pandas as pd

from .helper import (
    get_h2h_match_history,
    get_player_last_nplus1_matches,
    preprocess_data,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# GCS config constants
BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "msmballstars-data")
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
DATA_FOLDER = os.environ.get("DATA_FOLDER", "version1")
DATA_FILE = os.environ.get("DATA_FILE", "combined_atp_matches.csv")
GCS_CACHE = os.environ.get("GCS_CACHE")


def get_gcs_client():
    """Initialize and return GCS client"""
    if os.environ.get("ENV") == "test":
        return None

    client = storage.Client()
    return client


def read_csv_from_gcs(bucket, file_name):
    logging.info(f"Reading file: {file_name}")
    if GCS_CACHE:
        local_file_path = os.path.join(GCS_CACHE, file_name)
        if os.path.exists(local_file_path):
            logging.info(f"File found in local cache: {local_file_path}")
            return pd.read_csv(local_file_path)

    blob = bucket.blob(file_name)
    content = blob.download_as_text()
    # Write to local cache
    if GCS_CACHE:
        local_file_path = os.path.join(GCS_CACHE, file_name)
        # create all parent directories if they don't exist
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
        with open(local_file_path, "w") as f:
            f.write(content)

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


player_dfs, feature_cols = None, None


def initialize_data():
    global player_dfs, feature_cols
    player_dfs, feature_cols = load_data()


def get_match_data(
    player_a_id: str, player_b_id: str, lookback: int
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str]]:
    if player_dfs is None or feature_cols is None:
        initialize_data()

    player_a_previous_matches = get_player_last_nplus1_matches(
        player_dfs, player_a_id, lookback
    )
    player_b_previous_matches = get_player_last_nplus1_matches(
        player_dfs, player_b_id, lookback
    )
    h2h_match_history = get_h2h_match_history(player_dfs, player_a_id, player_b_id)

    return (
        player_a_previous_matches,
        player_b_previous_matches,
        h2h_match_history,
        feature_cols,
    )
