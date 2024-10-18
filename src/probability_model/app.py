import os

if os.environ.get("ENV") != "prod":
    from dotenv import load_dotenv

    load_dotenv("../.env.dev")

import logging
from typing import List

import fastapi
import torch
from google.cloud import storage
from pydantic import BaseModel

from .model import TennisLSTM

BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "default-bucket-name")
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
DATA_FOLDER = os.environ.get("DATA_FOLDER")
DATA_FILE = os.environ.get("DATA_FILE")
HIDDEN_SIZE = int(os.environ.get("HIDDEN_SIZE"))
NUM_LAYERS = int(os.environ.get("NUM_LAYERS"))


def read_file_from_gcs(bucket, file_name):
    logging.info(f"Reading file: {file_name}")
    blob = bucket.blob(file_name)
    pickle_data = blob.download_as_bytes()
    return pickle.loads(BytesIO(pickle_data).getvalue())


logging.info(f"Using GCS bucket: {BUCKET_NAME}")
logging.info(f"Using GCS credentials: {GOOGLE_APPLICATION_CREDENTIALS}")

# Check if GPU is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logging.info(f"Using device: {device}")

# Initialize GCS client
client = storage.Client()
bucket = client.bucket(BUCKET_NAME)


# Read data file
data = read_file_from_gcs(bucket, os.path.join(DATA_FOLDER, DATA_FILE))

# Initialize model
input_size = data["X1"].shape[-1]
h2h_size = data["H2H"].shape[-1]

# load the model from GCS
model_weights_file = f"{DATA_FOLDER}/prob_model.pt"
bucket.blob(model_weights_file).download_to_file(
    model_weights_file, content_type="application/octet-stream"
)

model = TennisLSTM(input_size, HIDDEN_SIZE, NUM_LAYERS, h2h_size)
model.load_state_dict(torch.load(model_weights_file))
model.to(device)


app = fastapi.FastAPI()


class PredictionResponse(BaseModel):
    player_a_win_probability: float


class PredictionRequest(BaseModel):
    player_a_last_10_matches: List[int]
    player_b_last_10_matches: List[int]
    head_to_head_match_history: List[int]


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    X1 = torch.tensor(request.player_a_last_10_matches, dtype=torch.float32)
    X2 = torch.tensor(request.player_b_last_10_matches, dtype=torch.float32)
    H2H = torch.tensor(request.head_to_head_match_history, dtype=torch.float32)
    output = model(X1, X2, H2H)
    return {"player_a_win_probability": float(output.item())}


@app.get("/health")
def health():
    return {"status": "ok"}
