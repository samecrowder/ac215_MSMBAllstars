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
    from .model import TennisLSTM
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
DATA_FILE = os.environ.get("DATA_FILE", "prob_model.pt ")
WEIGHTS_FILE = os.environ.get("WEIGHTS_FILE", "model_weights.pt")
HIDDEN_SIZE = int(os.environ.get("HIDDEN_SIZE", "256"))
NUM_LAYERS = int(os.environ.get("NUM_LAYERS", "2"))
GCS_CACHE = os.environ.get("GCS_CACHE")


def read_file_from_gcs_or_cache(bucket: storage.Bucket, file_name: str) -> bytes:
    """
    Read a file from GCS or local cache if it exists.
    /gcs_cache/msmballstars-data is where the data may be cached.
    """
    logging.info(f"Loading file: {file_name}")
    if GCS_CACHE:
        cache_dir = os.path.join(GCS_CACHE, BUCKET_NAME)
        local_file_path = os.path.join(cache_dir, file_name)
        
        # Create the cache directory structure if it doesn't exist
        try:
            os.makedirs(cache_dir, exist_ok=True)
            logging.info(f"Cache directory ensured: {cache_dir}")
        except Exception as e:
            logging.error(f"Failed to create cache directory: {e}")
            
        if os.path.exists(local_file_path):
            logging.info(f"File found in local cache: {local_file_path}")
            with open(local_file_path, "rb") as f:
                return f.read()
        else:
            logging.info(f"File not found in local cache: {local_file_path}")
            logging.info(f"Current directory contents: {os.listdir(cache_dir) if os.path.exists(cache_dir) else 'directory does not exist'}")
    else:
        logging.info("GCS_CACHE is not set, skipping local cache check")

    blob = bucket.blob(file_name)
    pickle_data = blob.download_as_bytes()
    if GCS_CACHE:
        try:
            # Ensure the full directory path exists
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            with open(local_file_path, "wb") as f:
                f.write(pickle_data)
            logging.info(f"Successfully cached file to: {local_file_path}")
            logging.info(f"Cache file size: {os.path.getsize(local_file_path)} bytes")
        except Exception as e:
            logging.error(f"Failed to write to cache: {e}")

    return pickle_data


def read_pt_file_from_gcs(bucket, file_name):
    file_content = read_file_from_gcs_or_cache(bucket, file_name)
    return torch.load(BytesIO(file_content), map_location=torch.device("cpu"))


def read_pkl_file_from_gcs(bucket, file_name):
    file_content = read_file_from_gcs_or_cache(bucket, file_name)
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
    X1: List[List[float]]
    X2: List[List[float]]
    H2H: List[float]


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    try:
        logging.info(f"Received prediction request: {request}")

        # Convert inputs to tensors
        X1 = torch.tensor(request.X1, dtype=torch.float32)
        X2 = torch.tensor(request.X2, dtype=torch.float32)
        H2H = torch.tensor(request.H2H, dtype=torch.float32).unsqueeze(0).to(device)

        logging.info(
            f"Input tensor shapes - X1: {X1.shape}, X2: {X2.shape}, H2H: {H2H.shape}"
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
            output = model(X1_scaled, X2_scaled, H2H)

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
