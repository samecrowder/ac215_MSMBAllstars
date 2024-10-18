#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

export IMAGE_NAME="atp-llm-service"
export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/../../../secrets/
export GCS_BUCKET_NAME="msmballstars-data"
export GCP_PROJECT="tennis-match-predictor"
export GCP_ZONE="us-central1-a"
export GOOGLE_APPLICATION_CREDENTIALS=/secrets/data-service-account.json
export LLM_PORT=8002

# Check to see if path to secrets is correct
if [ ! -f "$SECRETS_DIR/data-service-account.json" ]; then
    echo "data-service-account.json not found at the path you have provided."
    exit 1
fi

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f Dockerfile .

echo ""
echo "======================"
echo "Starting LLM service on port $LLM_PORT"
echo "======================"
echo ""

# Run docker-compose with the environment variables
docker-compose up --abort-on-container-exit
