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
export EXECUTOR_IMAGE_URI="us-docker.pkg.dev/vertex-ai/training/pytorch-xla.2-3.py310:latest"
export PYTHON_PACKAGE_URI="$GCS_BUCKET_URI/$TRAIN_TAR_DIR/$TRAINER_FILENAME"
export PYTHON_MODULE="trainer.task"
export ACCELERATOR_TYPE="NVIDIA_TESLA_T4"
export ACCELERATOR_COUNT=1
export GCP_REGION="us-east1"

# Training-specific environment variables
export DATA_FOLDER="version3"
export DATA_FILE="lite_npaware_training_data_lookback=10.pkl"
export TEST_SIZE=0.2
export BATCH_SIZE=32
export HIDDEN_SIZE=64
export NUM_LAYERS=2
export LR=0.001
export NUM_EPOCHS=100
export RUN_SWEEP=0
export VAL_F1_THRESHOLD=.63

# Read WANDB_KEY from JSON file
if [ ! -f "$SECRETS_DIR/wandb-key.json" ]; then
    echo "wandb-key.json not found at: $SECRETS_DIR/wandb-key.json"
    exit 1
fi

export WANDB_KEY=$(cat "$SECRETS_DIR/wandb-key.json" | jq -r '.key')

echo "WANDB_KEY: $WANDB_KEY"

# Create command line arguments string
export CMDARGS="--bucket-name=$BUCKET_NAME,\
--data-folder=$DATA_FOLDER,\
--data-file=$DATA_FILE,\
--test-size=$TEST_SIZE,\
--batch-size=$BATCH_SIZE,\
--hidden-size=$HIDDEN_SIZE,\
--num-layers=$NUM_LAYERS,\
--lr=$LR,\
--num-epochs=$NUM_EPOCHS,\
--run-sweep=$RUN_SWEEP,\
--val-f1-threshold=$VAL_F1_THRESHOLD,\
--wandb-key=$WANDB_KEY"

# Submit job to Vertex AI with command line arguments
gcloud ai custom-jobs create \
    --region=$GCP_REGION \
    --display-name=$DISPLAY_NAME \
    --python-package-uris=$PYTHON_PACKAGE_URI \
    --worker-pool-spec=machine-type=$MACHINE_TYPE,replica-count=$REPLICA_COUNT,executor-image-uri=$EXECUTOR_IMAGE_URI,python-module=$PYTHON_MODULE \
    --args=$CMDARGS