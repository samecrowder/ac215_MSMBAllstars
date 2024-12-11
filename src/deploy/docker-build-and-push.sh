#!/bin/bash

# Required environment variables:
# PROJECT_ID: GCP project ID
# SERVICE_NAME: Name of the service
# SERVICE_PATH: Path to the service
# DOCKERFILE: Name of the dockerfile
# IMAGE_TAG: Tag for the image (usually git SHA)

set -e

cd "$SERVICE_PATH"

echo "Building and pushing $SERVICE_NAME..."
docker build --platform linux/amd64 -f "$DOCKERFILE" -t "gcr.io/$PROJECT_ID/$SERVICE_NAME:$IMAGE_TAG" $BUILD_ARGS .
docker push "gcr.io/$PROJECT_ID/$SERVICE_NAME:$IMAGE_TAG"
docker tag "gcr.io/$PROJECT_ID/$SERVICE_NAME:$IMAGE_TAG" "gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"
docker push "gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"