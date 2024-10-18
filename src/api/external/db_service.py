from io import StringIO
import logging
import os
from typing import Any, List

from google.cloud import storage
import numpy as np
import pandas as pd
from pydantic import BaseModel


def preprocess_data(df):

    # Sort by date
    df = df.sort_values("tourney_date")

    # Select relevant features
    feature_cols = [
        col for col in df.columns if col.startswith("w_") or col.startswith("l_")
    ]

    # Create player-specific dataframes
    player_dfs = {}
    for player in set(df["winner_name"].unique()) | set(df["loser_name"].unique()):
        player_matches = df[
            (df["winner_name"] == player) | (df["loser_name"] == player)
        ].copy()
        player_matches["is_winner"] = (player_matches["winner_name"] == player).astype(
            int
        )
        player_matches["opponent"] = np.where(
            player_matches["winner_name"] == player,
            player_matches["loser_name"],
            player_matches["winner_name"],
        )
        player_dfs[player] = player_matches.reset_index()

    return player_dfs, feature_cols


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


class DataFrameModel(BaseModel):
    columns: List[str]
    data: List[List[Any]]


def get_player_last_nplus1_matches(player_id: str, n: int) -> DataFrameModel:
    df = player_dfs[player_id].tail(n + 1).reset_index()
    return DataFrameModel(columns=df.columns.tolist(), data=df.values.tolist())


def get_head_to_head_match_history(
    player_a_id: str, player_b_id: str
) -> DataFrameModel:
    df = player_dfs[player_a_id][player_dfs[player_a_id]["opponent"] == player_b_id]
    return DataFrameModel(columns=df.columns.tolist(), data=df.values.tolist())
