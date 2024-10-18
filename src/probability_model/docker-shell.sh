#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

export IMAGE_NAME="atp-model-service"
export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/../../../secrets/
export GCS_BUCKET_NAME="msmballstars-data-kc"
export GCP_PROJECT="tennis-match-predictor"
export GCP_ZONE="us-central1-a"
export GOOGLE_APPLICATION_CREDENTIALS=/secrets/data-service-account.json
export DATA_FOLDER="version1"
export DATA_FILE="prob_model.pt"
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

# Run docker-compose with the environment variables
docker-compose up --abort-on-container-exit
