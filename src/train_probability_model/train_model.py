import os
import pickle
import logging
from google.cloud import storage
import torch
from torch import nn
from io import BytesIO

from training_pipeline import create_data_loaders, train_model
from model import TennisLSTM

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# GCS
BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "default-bucket-name")
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
DATA_FOLDER = os.environ.get("DATA_FOLDER")
DATA_FILE = os.environ.get("DATA_FILE")
TEST_SIZE = float(os.environ.get("TEST_SIZE"))
BATCH_SIZE = int(os.environ.get("BATCH_SIZE"))
HIDDEN_SIZE = int(os.environ.get("HIDDEN_SIZE"))
NUM_LAYERS = int(os.environ.get("NUM_LAYERS"))
LR = float(os.environ.get("LR"))
NUM_EPOCHS = int(os.environ.get("NUM_EPOCHS"))


logging.info(f"Using GCS bucket: {BUCKET_NAME}")
logging.info(f"Using GCS credentials: {GOOGLE_APPLICATION_CREDENTIALS}")


def read_file_from_gcs(bucket, file_name):
    logging.info(f"Reading file: {file_name}")
    blob = bucket.blob(file_name)
    pickle_data = blob.download_as_bytes()
    return pickle.loads(BytesIO(pickle_data).getvalue())


def count_trainable_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def main():
    logging.info("Starting preprocessing script")

    # Check if GPU is available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logging.info(f"Using device: {device}")

    # Initialize GCS client
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    logging.info(f"Connected to GCS bucket: {BUCKET_NAME}")

    # Read data file
    data = read_file_from_gcs(bucket, os.path.join(DATA_FOLDER, DATA_FILE))

    # Create dataset loaders
    train_loader, test_loader = create_data_loaders(
        device,
        data["X1"],
        data["X2"],
        data["H2H"],
        data["y"],
        test_size=TEST_SIZE,
        batch_size=BATCH_SIZE,
    )

    # Initialize model
    input_size = data["X1"].shape[-1]
    h2h_size = data["H2H"].shape[-1]
    model = TennisLSTM(input_size, HIDDEN_SIZE, NUM_LAYERS, h2h_size).to(device)
    trainable_params = count_trainable_parameters(model)
    logging.info(f"Total number of trainable parameters: {trainable_params}")

    # Train model
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    train_model(model, train_loader, test_loader, criterion, optimizer, num_epochs=NUM_EPOCHS)

    # Save the model to a BytesIO object
    buffer = BytesIO()
    torch.save(model.state_dict(), buffer)
    buffer.seek(0)

    # Write the model to GCS
    output_file = f"{DATA_FOLDER}/prob_model.pt"
    logging.info(f"Writing model to {output_file}")
    bucket.blob(output_file).upload_from_file(
        buffer, content_type="application/octet-stream"
    )

    logging.info(f"Model successfully written to {output_file}")
    logging.info("Training and model saving completed")


if __name__ == "__main__":
    main()
