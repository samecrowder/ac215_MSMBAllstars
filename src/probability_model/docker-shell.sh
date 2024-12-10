#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

export IMAGE_NAME="atp-model-service"
export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/../../../secrets/
export GCS_BUCKET_NAME="msmballstars-data"
export GCP_PROJECT="tennis-match-predictor"
export GCP_ZONE="us-central1-a"
export GOOGLE_APPLICATION_CREDENTIALS=/secrets/data-service-account.json
export DATA_FOLDER="version5"
export DATA_FILE="training_data_lookback=10.pkl"
export WEIGHTS_FILE="prob_model.pt"
export HIDDEN_SIZE=32
export NUM_LAYERS=2
export MODEL_PORT=8001

# Check to see if path to secrets is correct
if [ ! -f "$SECRETS_DIR/data-service-account.json" ]; then
    echo "data-service-account.json not found at the path you have provided."
    exit 1
fi

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f Dockerfile .

echo ""
echo "======================"
echo "Starting model service on port $MODEL_PORT"
echo "======================"
echo ""

# Run the container
docker run --rm -it \
--name "$IMAGE_NAME" \
--mount type=bind,source="$BASE_DIR",target=/app \
--mount type=bind,source="$SECRETS_DIR",target=/secrets \
-e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
-e GCP_PROJECT="$GCP_PROJECT" \
-e GCP_ZONE=$GCP_ZONE \
-e GCS_BUCKET_NAME=$GCS_BUCKET_NAME \
-e DATA_FOLDER=$DATA_FOLDER \
-e DATA_FILE=$DATA_FILE \
-e WEIGHTS_FILE=$WEIGHTS_FILE \
-e HIDDEN_SIZE=$HIDDEN_SIZE \
-e NUM_LAYERS=$NUM_LAYERS \
-e PORT=$MODEL_PORT \
-p $MODEL_PORT:$MODEL_PORT \
$IMAGE_NAME
