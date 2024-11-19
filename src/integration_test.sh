#!/bin/bash

# Exit on any error
set -e

echo "🧹 Cleaning up any existing containers..."
docker compose down

echo "🏗️ Building containers..."
docker compose build

echo "🚀 Starting services..."
docker compose up -d

echo "⏳ Waiting for API to be ready..."
timeout=600  # 10 minutes in seconds
interval=5   # Check every 5 seconds
elapsed=0

while true; do
    if [ $elapsed -ge $timeout ]; then
        echo "❌ Timeout waiting for API to be ready"
        docker compose logs api  # Print API logs for debugging
        exit 1
    fi

    status_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo "failed")
    
    if [ "$status_code" = "200" ]; then
        echo "✅ API is ready!"
        break
    fi

    sleep $interval
    elapsed=$((elapsed + interval))
    echo "⏳ Still waiting for API... (${elapsed}s elapsed)"
done

echo "🎯 Testing prediction endpoint..."
predict_status_code=$(curl -s -o predict_response.json -w "%{http_code}" \
    -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d '{
        "player_a_id": "Roger Federer",
        "player_b_id": "Rafael Nadal",
        "lookback": 10
    }')

echo "Prediction Response (Status Code: $predict_status_code):"
cat predict_response.json | jq '.'

if [ "$predict_status_code" != "200" ]; then
    echo "❌ Prediction request failed with status code $predict_status_code"
    docker compose logs api
    rm predict_response.json
    exit 1
fi

echo "💬 Testing chat endpoint..."
chat_status_code=$(curl -s -o chat_response.json -w "%{http_code}" \
    -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{
        "query": "Who is more likely to win between Federer and Nadal on clay court?",
        "history": []
    }')

echo "Chat Response (Status Code: $chat_status_code):"
cat chat_response.json | jq '.'

if [ "$chat_status_code" != "200" ]; then
    echo "❌ Chat request failed with status code $chat_status_code"
    docker compose logs api
    rm predict_response.json chat_response.json
    exit 1
fi

echo "🎉 All integration tests passed successfully!"
rm predict_response.json chat_response.json
