import os
import pickle
import logging
from google.cloud import storage
import pandas as pd
import numpy as np
from tqdm import tqdm
from io import BytesIO, StringIO

from helper import create_matchup_data, preprocess_data

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


def read_csv_from_gcs(bucket, file_name):
    logging.info(f"Reading file: {file_name}")
    blob = bucket.blob(file_name)
    content = blob.download_as_text()
    return pd.read_csv(StringIO(content))


def main():
    logging.info("Starting preprocessing script")

    # Initialize GCS client
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    logging.info(f"Connected to GCS bucket: {BUCKET_NAME}")

    # Read data file
    df = read_csv_from_gcs(bucket, os.path.join(DATA_FOLDER, DATA_FILE))
    logging.info(f"Data shape: {df.shape}")

    # Create dataset
    df["tourney_date"] = pd.to_datetime(df["tourney_date"], format="%Y-%m-%d")
    player_dfs, feature_cols = preprocess_data(df)
    X1, X2, H2H, y = [], [], [], []
    for _, matchup in tqdm(df.iterrows()):
        winner = matchup["winner_name"]
        loser = matchup["loser_name"]
        date = matchup["tourney_date"]

        # Add winning match
        p1_features, p2_features, h2h_features = create_matchup_data(
            winner, loser, date, player_dfs, feature_cols
        )
        X1.append(p1_features)
        X2.append(p2_features)
        H2H.append(h2h_features)
        y.append(1)  # Winner is labeled as 1

        # Add losing match (swap players)
        p2_features, p1_features, h2h_features_swapped = create_matchup_data(
            loser, winner, date, player_dfs, feature_cols
        )
        X1.append(p1_features)
        X2.append(p2_features)
        H2H.append(h2h_features_swapped)
        y.append(0)  # Loser is labeled as 0

    # Convert to numpy arrays
    X1 = np.array(X1)
    X2 = np.array(X2)
    H2H = np.array(H2H)
    y = np.array(y)

    # Create object to save
    data = {
        "X1": X1,
        "X2": X2,
        "H2H": H2H,
        "y": y,
    }
    serialized_data = pickle.dumps(data)
    file_obj = BytesIO(serialized_data)

    # Write the combined data to a new CSV in the next version folder
    output_file = f"{DATA_FOLDER}/training_data.pkl"
    logging.info(f"Writing combined data to {output_file}")
    bucket.blob(output_file).upload_from_file(file_obj, content_type='application/octet-stream')

    logging.info(f"Combined data successfully written to {output_file}")
    logging.info("Preprocessing completed")


if __name__ == "__main__":
    main()
