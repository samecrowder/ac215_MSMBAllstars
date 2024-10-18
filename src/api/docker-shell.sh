#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

export IMAGE_NAME="atp-predictor-app"
export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/../../../secrets/
export GCP_PROJECT="tennis-match-predictor"
export GCP_ZONE="us-central1-a"
export GCS_BUCKET_NAME="msmballstars-data-kc"
export DATA_FOLDER="version1"
export DATA_FILE="combined_atp_matches.csv"
export GOOGLE_APPLICATION_CREDENTIALS=/secrets/data-service-account.json
export API_PORT=8000
# Check to see if path to secrets is correct
if [ ! -f "$SECRETS_DIR/data-service-account.json" ]; then
    echo "data-service-account.json not found at the path you have provided."
    exit 1
fi

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f Dockerfile .


echo ""
echo "======================"
echo "Starting API service on port $API_PORT"
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
-e ENV=prod \
-e MODEL_SERVICE_URL=http://127.0.0.1:8001 \
-e LLM_SERVICE_URL=http://127.0.0.1:8002 \
-e PORT=$API_PORT \
-p $API_PORT:$API_PORT \
$IMAGE_NAME
