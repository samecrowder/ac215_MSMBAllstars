#!/usr/bin/env zsh

# the high level structure of this script needs to be kept in sync
# with the deploy.yml workflow. we don't call it directly because we want
# to have parallel builds for each service in the workflow.

# Required environment variables:
# PROJECT_ID: GCP project ID
# IMAGE_TAG: Tag for the image (usually git SHA)

set -e

# Configuration
REGION="us-central1"
SERVICES=(
    "api:Dockerfile:src/api"
    "probability-model:Dockerfile:src/probability_model"
    "llm:Dockerfile:src/llm"
    "ollama:ollama.Dockerfile:src/llm"
)

# Setup GCP authentication
echo "Setting up GCP authentication..."
gcloud auth configure-docker

# Build and push all services sequentially
for service in $SERVICES; do
    IFS=: read SERVICE_NAME DOCKERFILE SERVICE_PATH <<< $service
    
    echo "\n=== Building $SERVICE_NAME ===\n"
    export SERVICE_NAME DOCKERFILE SERVICE_PATH
    if ! ./docker-build-and-push.zsh; then
        echo "Failed to build $SERVICE_NAME"
        exit 1
    fi
done

./ansible-deploy.zsh
