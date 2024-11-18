import os
import json
import pickle
import logging
from google.cloud import storage
import torch
from torch import nn
from io import BytesIO
import wandb

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
WANDB_KEY = os.environ.get("WANDB_KEY")


logging.info(f"Using GCS bucket: {BUCKET_NAME}")
logging.info(f"Using GCS credentials: {GOOGLE_APPLICATION_CREDENTIALS}")


def read_file_from_gcs(bucket, file_name):
    logging.info(f"Reading file: {file_name}")
    blob = bucket.blob(file_name)
    pickle_data = blob.download_as_bytes()
    return pickle.loads(BytesIO(pickle_data).getvalue())


def count_trainable_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


class WandbCallback:
    def __init__(self):
        self.best_val_f1 = float('-inf')
        
    def on_epoch_end(self, epoch, train_loss, val_loss, train_acc, val_acc,
                     train_precision, val_precision, train_recall, val_recall,
                     train_f1, val_f1):
        wandb.log({
            "epoch": epoch,
            "train_loss": train_loss,
            "val_loss": val_loss,
            "train_accuracy": train_acc,
            "val_accuracy": val_acc,
            "train_precision": train_precision,
            "val_precision": val_precision,
            "train_recall": train_recall,
            "val_recall": val_recall,
            "train_f1": train_f1,
            "val_f1": val_f1
        })
        
        # Track best F1 score instead of loss
        if val_f1 > self.best_val_f1:
            self.best_val_f1 = val_f1
            wandb.run.summary["best_val_f1"] = val_f1


def main():
    logging.info("Starting preprocessing script")

    # Initialize wandb
    wandb.login(key=WANDB_KEY)
    wandb.init(
        project="tennis-match-predictor",
        config={
            "test_size": TEST_SIZE,
            "batch_size": BATCH_SIZE,
            "hidden_size": HIDDEN_SIZE,
            "num_layers": NUM_LAYERS,
            "learning_rate": LR,
            "num_epochs": NUM_EPOCHS
        }
    )

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
    wandb.watch(model)
    train_model(model, train_loader, test_loader, criterion, optimizer, num_epochs=NUM_EPOCHS, callback=WandbCallback())

    # Save model directly to GCS using BytesIO
    gcs_output_path = f"{DATA_FOLDER}/prob_model.pt"
    buffer = BytesIO()
    torch.save(model.state_dict(), buffer)
    buffer.seek(0)
    
    logging.info(f"Uploading model to Google Cloud Storage at: {gcs_output_path}")
    bucket.blob(gcs_output_path).upload_from_file(buffer, content_type="application/octet-stream")
    logging.info("Successfully uploaded model to Google Cloud Storage")
    
    wandb.finish()

    logging.info("=== Training Pipeline Complete ===")


if __name__ == "__main__":
    main()
