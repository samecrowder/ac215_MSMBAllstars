#!/bin/bash

# Set base directory and secrets directory
export BASE_DIR=$(pwd)
export SECRETS_DIR="$BASE_DIR/../../../secrets"

# Set environment variables
export BUCKET_NAME="msmballstars-data"
export TRAIN_TAR_DIR="train_tar"
export TRAINER_FILENAME="tennis-trainer.tar.gz"
export GCS_BUCKET_URI="gs://$BUCKET_NAME"
export UUID=$(openssl rand -hex 6)
export DISPLAY_NAME="tennis_training_job_$UUID"
export MACHINE_TYPE="n1-standard-4"
export REPLICA_COUNT=1
# export EXECUTOR_IMAGE_URI="us-docker.pkg.dev/vertex-ai/training/pytorch-gpu.1-13:latest"
export EXECUTOR_IMAGE_URI="us-docker.pkg.dev/vertex-ai/training/pytorch-xla.2-3.py310:latest"
export PYTHON_PACKAGE_URI="$GCS_BUCKET_URI/$TRAIN_TAR_DIR/$TRAINER_FILENAME"
export PYTHON_MODULE="trainer.train_model"
export ACCELERATOR_TYPE="NVIDIA_TESLA_T4"
export ACCELERATOR_COUNT=1
export GCP_REGION="us-east1"

# Training-specific environment variables
export TEST_SIZE=0.2
export BATCH_SIZE=32
export HIDDEN_SIZE=64
export NUM_LAYERS=2
export LR=0.001
export NUM_EPOCHS=10
export DATA_FOLDER="data"
export DATA_FILE="processed_data.pkl"

# Read WANDB_KEY from JSON file
if [ ! -f "$SECRETS_DIR/wandb-key.json" ]; then
    echo "wandb-key.json not found at: $SECRETS_DIR/wandb-key.json"
    exit 1
fi

export WANDB_KEY=$(cat "$SECRETS_DIR/wandb-key.json" | jq -r '.key')

# Submit job to Vertex AI using updated syntax
gcloud ai custom-jobs create \
    --region=$GCP_REGION \
    --display-name=$DISPLAY_NAME \
    --python-package-uris=$PYTHON_PACKAGE_URI \
    --worker-pool-spec="machine-type=$MACHINE_TYPE,\
replica-count=$REPLICA_COUNT,\
executor-image-uri=$EXECUTOR_IMAGE_URI,\
python-module=$PYTHON_MODULE"

# python-module=$PYTHON_MODULE,\
# accelerator-type=$ACCELERATOR_TYPE,\
# accelerator-count=$ACCELERATOR_COUNT"