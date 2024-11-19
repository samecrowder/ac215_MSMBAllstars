# 1. Build and tag images using docker compose
docker compose build

# 2. Tag images for Google Container Registry
docker tag src-api:latest gcr.io/tennis-match-predictor/api:latest
docker tag src-probability_model:latest gcr.io/tennis-match-predictor/probability-model:latest
docker tag src-llm:latest gcr.io/tennis-match-predictor/llm:latest

# 3. Push to GCR
docker push gcr.io/tennis-match-predictor/api:latest
docker push gcr.io/tennis-match-predictor/probability-model:latest
docker push gcr.io/tennis-match-predictor/llm:latest

# 4. Deploy to Cloud Run using environment variables from docker-compose
# Deploy API
gcloud run deploy api \
  --image gcr.io/tennis-match-predictor/api:latest \
  --platform managed \
  --region us-central1 \
  --set-env-vars="$(docker compose config | yq '.services.api.environment | with_entries(select(.key != "PORT")) | to_entries | map(.key + "=" + .value) | join(",")')"

# Deploy Probability Model
gcloud run deploy probability-model \
  --image gcr.io/tennis-match-predictor/probability-model:latest \
  --platform managed \
  --region us-central1 \
  --set-env-vars="$(docker compose config | yq '.services.probability_model.environment | with_entries(select(.key != "PORT")) | to_entries | map(.key + "=" + .value) | join(",")')"

# Deploy LLM
gcloud run deploy llm \
  --image gcr.io/tennis-match-predictor/llm:latest \
  --platform managed \
  --region us-central1 \
  --set-env-vars="$(docker compose config | yq '.services.llm.environment | with_entries(select(.key != "PORT")) | to_entries | map(.key + "=" + .value) | join(",")')"
