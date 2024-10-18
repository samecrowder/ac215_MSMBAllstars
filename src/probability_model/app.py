from io import BytesIO
import os
import pickle

if os.environ.get("ENV") != "prod":
    from dotenv import load_dotenv

    load_dotenv("../.env.dev")

import logging
from typing import Any, List

import fastapi
import torch
from google.cloud import storage
import pandas as pd
from pydantic import BaseModel
from sklearn.preprocessing import StandardScaler


from .model import TennisLSTM

BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "default-bucket-name")
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
DATA_FOLDER = os.environ.get("DATA_FOLDER")
DATA_FILE = os.environ.get("DATA_FILE")
WEIGHTS_FILE = os.environ.get("WEIGHTS_FILE")
HIDDEN_SIZE = int(os.environ.get("HIDDEN_SIZE"))
NUM_LAYERS = int(os.environ.get("NUM_LAYERS"))


def read_pt_file_from_gcs(bucket, file_name):
    logging.info(f"Reading file: {file_name}")
    blob = bucket.blob(file_name)
    file_content = blob.download_as_bytes()
    return torch.load(BytesIO(file_content), map_location=torch.device("cpu"))


def read_pkl_file_from_gcs(bucket, file_name):
    logging.info(f"Reading file: {file_name}")
    blob = bucket.blob(file_name)
    file_content = blob.download_as_bytes()
    return pickle.loads(BytesIO(file_content).getvalue())


logging.info(f"Using GCS bucket: {BUCKET_NAME}")
logging.info(f"Using GCS credentials: {GOOGLE_APPLICATION_CREDENTIALS}")

# Check if GPU is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logging.info(f"Using device: {device}")

# Initialize GCS client
client = storage.Client()
bucket = client.bucket(BUCKET_NAME)

# Read data file
data = read_pkl_file_from_gcs(bucket, os.path.join(DATA_FOLDER, DATA_FILE))
X1 = data["X1"]
X2 = data["X2"]
H2H = data["H2H"]

# Assuming X1 and X2 are 3D arrays with shape (samples, time_steps, features)
samples, time_steps, features = X1.shape

# Reshape X1 and X2 to 2D
X1_reshaped = X1.reshape(-1, features)
X2_reshaped = X2.reshape(-1, features)

# TODO: save scaler objects during training time and fetch from GCS

# Initialize scalers
scaler_X1 = StandardScaler()
scaler_X2 = StandardScaler()
# scaler_H2H = StandardScaler()

# Fit and transform X1 and X2
scaler_X1.fit(X1_reshaped)
scaler_X2.fit(X2_reshaped)
# H2H_scaled = scaler_H2H.fit(H2H_reshaped)

# Initialize model
input_size = X1.shape[-1]
h2h_size = H2H.shape[-1]

# Load the model weights from GCS
weights = read_pt_file_from_gcs(bucket, os.path.join(DATA_FOLDER, WEIGHTS_FILE))
model = TennisLSTM(input_size, HIDDEN_SIZE, NUM_LAYERS, h2h_size)
model.load_state_dict(weights)
model.to(device)


app = fastapi.FastAPI()


class PredictionResponse(BaseModel):
    player_a_win_probability: float


class PredictionRequest(BaseModel):
    X1: List[float]
    X2: List[float]
    H2H: List[float]


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    X1 = request.X1
    X2 = request.X2
    H2H = request.H2H
    output = model(X1, X2, H2H)
    return {"player_a_win_probability": float(output.item())}


@app.get("/health")
def health():
    return {"status": "ok"}
