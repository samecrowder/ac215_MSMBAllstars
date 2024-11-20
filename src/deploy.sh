#!/bin/bash

# Exit on any error
set -e

# Check if running in CI or with correct service account
CURRENT_ACCOUNT=$(gcloud config get-value account)
if [ "$RUNNING_FROM_CI" != "true" ] && [ "$CURRENT_ACCOUNT" != "super-admin-account@tennis-match-predictor.iam.gserviceaccount.com" ]; then
    echo "❌ Error: Must be running in CI or authenticated as super-admin-account@tennis-match-predictor.iam.gserviceaccount.com"
    echo "Current account: $CURRENT_ACCOUNT"
    exit 1
fi

echo "✅ Authentication check passed"
echo "🔑 Deploying with account: $CURRENT_ACCOUNT"

# Build and tag images
docker compose build

# Tag images for Google Container Registry
docker tag src-api:latest gcr.io/tennis-match-predictor/api:latest
docker tag src-probability_model:latest gcr.io/tennis-match-predictor/probability-model:latest
docker tag src-llm:latest gcr.io/tennis-match-predictor/llm:latest
docker tag src-web:latest gcr.io/tennis-match-predictor/web:latest

# Push to GCR
docker push gcr.io/tennis-match-predictor/api:latest
docker push gcr.io/tennis-match-predictor/probability-model:latest
docker push gcr.io/tennis-match-predictor/llm:latest
docker push gcr.io/tennis-match-predictor/web:latest

# Get Ollama URL. We assume that ollama is already deployed.
OLLAMA_URL=$(gcloud run services describe ollama --platform managed --region us-central1 --format 'value(status.url)')
echo "OLLAMA_URL: $OLLAMA_URL"

# Deploy LLM with Ollama URL
gcloud run deploy llm \
    --image gcr.io/tennis-match-predictor/llm:latest \
    --platform managed \
    --region us-central1 \
    --set-env-vars="OLLAMA_HOST=${OLLAMA_URL},$(docker compose config | yq '.services.llm.environment | with_entries(select(.key != "PORT" and .key != "GOOGLE_APPLICATION_CREDENTIALS")) | to_entries | map(.key + "=" + .value) | join(",")')" \
    --set-secrets="/secrets/super-admin-key.json=super-admin-key:latest"

# Get LLM URL
LLM_URL=$(gcloud run services describe llm --platform managed --region us-central1 --format 'value(status.url)')
echo "LLM_URL: $LLM_URL"

# Deploy Probability Model
gcloud run deploy probability-model \
    --image gcr.io/tennis-match-predictor/probability-model:latest \
    --platform managed \
    --region us-central1 \
    --set-env-vars="$(docker compose config | yq '.services.probability_model.environment | with_entries(select(.key != "PORT" and .key != "GOOGLE_APPLICATION_CREDENTIALS")) | to_entries | map(.key + "=" + .value) | join(",")')" \
    --set-secrets="/secrets/super-admin-key.json=super-admin-key:latest"

# Get Probability Model URL
PROB_MODEL_URL=$(gcloud run services describe probability-model --platform managed --region us-central1 --format 'value(status.url)')
echo "PROB_MODEL_URL: $PROB_MODEL_URL"

# Deploy API with updated service URLs
gcloud run deploy api \
    --image gcr.io/tennis-match-predictor/api:latest \
    --platform managed \
    --region us-central1 \
    --set-env-vars="ENV=prod,MODEL_BASE_URL=${PROB_MODEL_URL},LLM_BASE_URL=${LLM_URL},$(docker compose config | yq '.services.api.environment | with_entries(select(.key != "PORT" and .key != "GOOGLE_APPLICATION_CREDENTIALS" and .key != "MODEL_HOST" and .key != "LLM_HOST" and .key != "ENV")) | to_entries | map(.key + "=" + .value) | join(",")')" \
    --set-secrets="/secrets/super-admin-key.json=super-admin-key:latest"
