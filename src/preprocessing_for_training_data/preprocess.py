import os
import pickle
import logging
from google.cloud import storage
import pandas as pd
import numpy as np
from tqdm import tqdm
from io import BytesIO, StringIO

from helper import (
    create_matchup_data,
    get_player_last_nplus1_matches_since_date,
    preprocess_data,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# GCS
BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "default-bucket-name")
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
DATA_FOLDER = os.environ.get("DATA_FOLDER")
DATA_FILE = os.environ.get("DATA_FILE")
LOOKBACK = int(os.environ.get("LOOKBACK"))


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

    local_output_file = f"./training_data_lookback={LOOKBACK}.pkl"
    if not os.path.exists(local_output_file):

        # Read data file
        df = read_csv_from_gcs(bucket, os.path.join(DATA_FOLDER, DATA_FILE))
        logging.info(f"Data shape: {df.shape}")

        # Create dataset
        df["tourney_date"] = pd.to_datetime(df["tourney_date"], format="%Y-%m-%d")
        player_dfs, feature_cols = preprocess_data(df)
        X1, X2, M1, M2, y = [], [], [], [], []  # M1, M2 are opponent masks

        for _, matchup in tqdm(df.iloc[:10000].iterrows()):
            winner = matchup["winner_name"]
            loser = matchup["loser_name"]
            date = matchup["tourney_date"]

            winner_history = get_player_last_nplus1_matches_since_date(
                player_dfs, winner, LOOKBACK, date
            )
            loser_history = get_player_last_nplus1_matches_since_date(
                player_dfs, loser, LOOKBACK, date
            )

            # Skip if either player has fewer matches than LOOKBACK
            if len(winner_history) < LOOKBACK + 1 or len(loser_history) < LOOKBACK + 1:
                continue

            # Create matchup data with opponent masks
            winner_features, loser_features, winner_mask, loser_mask = (
                create_matchup_data(
                    winner_history, loser_history, feature_cols, LOOKBACK
                )
            )

            # Add winning match
            X1.append(winner_features)
            X2.append(loser_features)
            M1.append(winner_mask)
            M2.append(loser_mask)
            y.append(1)  # Winner (X1) beats Loser (X2)

            # Add losing match by swapping players
            # Even though model architecture ensures P(B beats A) = 1 - P(A beats B),
            # we need both y=0 and y=1 samples during training for the loss function
            # to learn properly and place the decision boundary correctly
            X1.append(loser_features.copy())
            X2.append(winner_features.copy())
            M1.append(loser_mask.copy())
            M2.append(winner_mask.copy())
            y.append(0)  # Loser (X1) loses to Winner (X2)

            data = {
                "X1": np.array(X1),
                "X2": np.array(X2),
                "M1": np.array(M1),
                "M2": np.array(M2),
                "y": np.array(y),
            }

            with open(local_output_file, "wb") as f:
                pickle.dump(data, f)

    # Read local pkl data file
    local_output_file = f"./training_data_lookback={LOOKBACK}.pkl"
    with open(local_output_file, "rb") as f:
        data = pickle.load(f)

    serialized_data = pickle.dumps(data)
    file_obj = BytesIO(serialized_data)

    # Write the combined data to a new CSV in the next version folder
    print("writing to GCS")
    output_file = f"{DATA_FOLDER}/training_data_lookback={LOOKBACK}.pkl"
    logging.info(f"Writing combined data to {output_file}")
    bucket.blob(output_file).upload_from_file(
        file_obj, content_type="application/octet-stream"
    )

    logging.info(f"Combined data successfully written to {output_file}")
    logging.info("Preprocessing completed")


if __name__ == "__main__":
    main()
