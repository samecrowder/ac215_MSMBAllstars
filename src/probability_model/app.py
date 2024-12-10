from io import BytesIO
import os
import pickle
from typing import List
import logging

import fastapi
import torch

from google.cloud import storage
from pydantic import BaseModel
from sklearn.preprocessing import StandardScaler

if os.environ.get("ENV") != "test":
    from ac215_MSMBAllstars.src.probability_model.model import TennisLSTM
else:
    # Mock TennisLSTM for non-prod environments
    class TennisLSTM:
        def __init__(self, *args, **kwargs):
            pass

        def to(self, *args, **kwargs):
            return self

        def load_state_dict(self, *args, **kwargs):
            pass

        def eval(self):
            pass

        def __call__(self, *args, **kwargs):
            return torch.tensor([0.5])


if os.environ.get("ENV") != "prod":
    from dotenv import load_dotenv

    load_dotenv("../.env.dev")

    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    print("Development environment detected: Forcing CPU mode")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True,
)


BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "msmballstars-data")
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", None)
DATA_FOLDER = os.environ.get("DATA_FOLDER", "version1")
DATA_FILE = os.environ.get("DATA_FILE", "combined_atp_matches.csv")
WEIGHTS_FILE = os.environ.get("WEIGHTS_FILE", "prob_model.pt")
HIDDEN_SIZE = int(os.environ.get("HIDDEN_SIZE", "256"))
NUM_LAYERS = int(os.environ.get("NUM_LAYERS", "2"))


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

if os.environ.get("ENV") != "test":
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
    M1 = data["M1"]
    M2 = data["M2"]

    # Assuming X1 and X2 are 3D arrays with shape (samples, time_steps, features)
    samples, time_steps, features = X1.shape

    # Reshape X1 and X2 to 2D
    X1_reshaped = X1.reshape(-1, features)
    X2_reshaped = X2.reshape(-1, features)

    # Initialize scalers
    scaler_X1 = StandardScaler()
    scaler_X2 = StandardScaler()

    # Fit and transform X1 and X2
    scaler_X1.fit(X1_reshaped)
    scaler_X2.fit(X2_reshaped)

    # Initialize model
    input_size = X1.shape[-1]

    # Load the model weights from GCS
    weights = read_pt_file_from_gcs(bucket, os.path.join(DATA_FOLDER, WEIGHTS_FILE))
    model = TennisLSTM(input_size, HIDDEN_SIZE, NUM_LAYERS)
    model.load_state_dict(weights)
    model.to(device)


app = fastapi.FastAPI()


class PredictionResponse(BaseModel):
    player_a_win_probability: float


class PredictionRequest(BaseModel):
    X1: List[List[float]]
    X2: List[List[float]]
    M1: List[float]
    M2: List[float]


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    try:
        logging.info(f"Received prediction request: {request}")

        # Convert inputs to tensors
        X1 = torch.tensor(request.X1, dtype=torch.float32)
        X2 = torch.tensor(request.X2, dtype=torch.float32)
        M1 = torch.tensor(request.M1, dtype=torch.float32).to(device)
        M2 = torch.tensor(request.M2, dtype=torch.float32).to(device)

        logging.info(
            f"Input tensor shapes - X1: {X1.shape}, X2: {X2.shape}, M1: {M1.shape}, M2: {M2.shape}"
        )

        # Scale the inputs and add batch dimension
        X1_scaled = (
            torch.tensor(scaler_X1.transform(X1.cpu().numpy()), dtype=torch.float32)
            .unsqueeze(0)
            .to(device)
        )
        X2_scaled = (
            torch.tensor(scaler_X2.transform(X2.cpu().numpy()), dtype=torch.float32)
            .unsqueeze(0)
            .to(device)
        )
        # Ensure model is in eval mode
        model.eval()

        with torch.no_grad():
            output, _ = model(X1_scaled, X2_scaled, M1, M2)

        logging.info(f"Model output: {output}")

        result = {"player_a_win_probability": float(output.item())}
        logging.info(f"Returning prediction: {result}")

        return result
    except Exception as e:
        logging.error(f"Error during prediction: {str(e)}", exc_info=True)
        raise fastapi.HTTPException(
            status_code=500, detail=f"Prediction failed: {str(e)}"
        )


@app.get("/health")
def health():
    return {"status": "ok"}
