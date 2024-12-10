#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

export IMAGE_NAME=${IMAGE_NAME:-"preprocessing-atp-data"}
export BASE_DIR=$(pwd)
export SECRETS_DIR=${SECRETS_DIR:-"$BASE_DIR/../../../secrets"}
export GCP_PROJECT=${GCP_PROJECT:-"tennis-match-predictor"}
export GCP_ZONE=${GCP_ZONE:-"us-central1-a"}
export GCS_BUCKET_NAME=${GCS_BUCKET_NAME:-"msmballstars-data"}
export RAW_DATA_FOLDER=${RAW_DATA_FOLDER:-"raw_data"}
export GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS:-"/secrets/data-service-account.json"}

# Check to see if path to secrets is correct
if [ ! -f "$SECRETS_DIR/data-service-account.json" ]; then
    echo "data-service-account.json not found at the path you have provided."
    exit 1
fi

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f Dockerfile .

echo "Host GOOGLE_APPLICATION_CREDENTIALS: $GOOGLE_APPLICATION_CREDENTIALS"

# Run the container
docker run --rm -it \
--mount type=bind,source="$BASE_DIR",target=/app \
--mount type=bind,source="$SECRETS_DIR",target=/secrets \
-e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
-e GCP_PROJECT="$GCP_PROJECT" \
-e GCP_ZONE=$GCP_ZONE \
-e GCS_BUCKET_NAME=$GCS_BUCKET_NAME \
-e RAW_DATA_FOLDER=$RAW_DATA_FOLDER \
-e DEV=1 $IMAGE_NAME
