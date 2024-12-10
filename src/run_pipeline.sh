#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

echo "🎾 Starting Tennis Match Prediction Pipeline 🎾"

# Set common environment variables
export GCP_PROJECT="tennis-match-predictor"
export GCP_ZONE="us-central1-a"
export GCS_BUCKET_NAME="msmballstars-data"

export LOOKBACK=10

# Function to get the latest version from GCS
get_latest_version() {
    # List all version* directories, sort them, and get the latest one
    latest_version=$(gsutil ls gs://$GCS_BUCKET_NAME/ | grep 'version[0-9]' | sort -V | tail -n 1)
    if [ -z "$latest_version" ]; then
        echo "No version directories found in gs://$GCS_BUCKET_NAME/"
        exit 1
    fi
    # Remove trailing slash and get just the folder name
    latest_version=$(basename ${latest_version%/})
    echo $latest_version
}

# Step 1: Run preprocessing
echo "Step 1: Running initial preprocessing..."
cd preprocessing
export IMAGE_NAME="preprocessing-atp-data"
export RAW_DATA_FOLDER="raw_data"
./docker-shell.sh
unset GOOGLE_APPLICATION_CREDENTIALS
echo "✅ Initial preprocessing complete!"

# Step 1 Part 2: Get most recent version from GCS
echo "Getting latest version from GCS..."
export GOOGLE_APPLICATION_CREDENTIALS="../../secrets/data-service-account.json"
export DATA_FOLDER=$(get_latest_version)
unset GOOGLE_APPLICATION_CREDENTIALS
echo "Using version: $DATA_FOLDER"

# Step 2: Run preprocessing for training data
echo "Step 2: Running preprocessing for training data..."
cd ../preprocessing_for_training_data
export IMAGE_NAME="preprocessing-for-training-data"
export DATA_FILE="combined_atp_matches.csv"
./docker-shell.sh
unset GOOGLE_APPLICATION_CREDENTIALS
echo "✅ Training data preprocessing complete!"

# Step 3: Run model training
echo "Step 3: Running model training..."
cd ../train_probability_model
export IMAGE_NAME="train-probability-model"
export DATA_FILE="training_data_lookback=$LOOKBACK.pkl"
export TEST_SIZE=0.2
export BATCH_SIZE=32
export HIDDEN_SIZE=32
export NUM_LAYERS=2
export LR=0.001
export NUM_EPOCHS=30
export RUN_SWEEP=0
export VAL_F1_THRESHOLD=.63
./docker-shell.sh
unset GOOGLE_APPLICATION_CREDENTIALS
echo "✅ Model training complete!"

echo "🎉 Pipeline completed successfully! 🎉"