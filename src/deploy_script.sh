#!/bin/bash

# Build and tag images
docker compose build

# Tag images for Google Container Registry
docker tag src-api:latest gcr.io/tennis-match-predictor/api:latest
docker tag src-probability_model:latest gcr.io/tennis-match-predictor/probability-model:latest
docker tag src-llm:latest gcr.io/tennis-match-predictor/llm:latest

# Push to GCR
docker push gcr.io/tennis-match-predictor/api:latest
docker push gcr.io/tennis-match-predictor/probability-model:latest
docker push gcr.io/tennis-match-predictor/llm:latest

# Deploy API
gcloud run deploy api \
    --image gcr.io/tennis-match-predictor/api:latest \
    --platform managed \
    --region us-central1 \
    --set-env-vars="$(docker compose config | yq '.services.api.environment | with_entries(select(.key != "PORT" and .key != "GOOGLE_APPLICATION_CREDENTIALS")) | to_entries | map(.key + "=" + .value) | join(",")')" \
    --set-secrets="/secrets/super-admin-key.json=super-admin-key:latest"

# Deploy Probability Model
gcloud run deploy probability-model \
    --image gcr.io/tennis-match-predictor/probability-model:latest \
    --platform managed \
    --region us-central1 \
    --set-env-vars="$(docker compose config | yq '.services.probability_model.environment | with_entries(select(.key != "PORT" and .key != "GOOGLE_APPLICATION_CREDENTIALS")) | to_entries | map(.key + "=" + .value) | join(",")')" \
    --set-secrets="/secrets/super-admin-key.json=super-admin-key:latest"

# Deploy LLM
gcloud run deploy llm \
    --image gcr.io/tennis-match-predictor/llm:latest \
    --platform managed \
    --region us-central1 \
    --set-env-vars="$(docker compose config | yq '.services.llm.environment | with_entries(select(.key != "PORT" and .key != "GOOGLE_APPLICATION_CREDENTIALS")) | to_entries | map(.key + "=" + .value) | join(",")')" \
    --set-secrets="/secrets/super-admin-key.json=super-admin-key:latest"
