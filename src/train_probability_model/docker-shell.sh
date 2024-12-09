#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

export IMAGE_NAME="train-probability-model"
export BASE_DIR=$(pwd)
export SECRETS_DIR="$BASE_DIR/../../../secrets"
export GCP_PROJECT="tennis-match-predictor"
export GCP_ZONE="us-central1-a"
export GCS_BUCKET_NAME="msmballstars-data"
export DATA_FOLDER="version3"
export DATA_FILE="training_data_lookback=10.pkl"
export TEST_SIZE=.2
export BATCH_SIZE=32
export HIDDEN_SIZE=32
export NUM_LAYERS=2
export LR=0.001
export NUM_EPOCHS=30
export GOOGLE_APPLICATION_CREDENTIALS=/secrets/model-training-account.json

# Read WANDB_KEY from JSON file
if [ ! -f "$SECRETS_DIR/wandb-key.json" ]; then
    echo "wandb-key.json not found at: $SECRETS_DIR/wandb-key.json"
    exit 1
fi

export WANDB_KEY=$(cat "$SECRETS_DIR/wandb-key.json" | jq -r '.key')

# Check if WANDB_KEY was successfully read
if [ -z "$WANDB_KEY" ]; then
    echo "Failed to read WANDB_KEY from wandb-key.json"
    exit 1
fi

# Check to see if path to secrets is correct
if [ ! -f "$SECRETS_DIR/data-service-account.json" ]; then
    echo "data-service-account.json not found at the path you have provided."
    exit 1
fi

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME --platform=linux/arm64/v8 -f Dockerfile .

echo "Host GOOGLE_APPLICATION_CREDENTIALS: $GOOGLE_APPLICATION_CREDENTIALS"

# Run the container
docker run --rm -it \
--mount type=bind,source="$BASE_DIR",target=/app \
--mount type=bind,source="$SECRETS_DIR",target=/secrets \
-e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
-e GCP_PROJECT="$GCP_PROJECT" \
-e GCP_ZONE=$GCP_ZONE \
-e GCS_BUCKET_NAME=$GCS_BUCKET_NAME \
-e DATA_FOLDER=$DATA_FOLDER \
-e DATA_FILE=$DATA_FILE \
-e TEST_SIZE=$TEST_SIZE \
-e BATCH_SIZE=$BATCH_SIZE \
-e HIDDEN_SIZE=$HIDDEN_SIZE \
-e NUM_LAYERS=$NUM_LAYERS \
-e LR=$LR \
-e NUM_EPOCHS=$NUM_EPOCHS \
-e WANDB_KEY=$WANDB_KEY \
-e DEV=1 $IMAGE_NAME
 