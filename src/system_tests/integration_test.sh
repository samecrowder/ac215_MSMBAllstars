#!/bin/bash

# Exit on any error
set -e

# Source common functions
source "$(dirname "$0")/test_utils.sh"

setup_cache_directory
setup_containers

# Wait for all services
wait_for_all_services

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

# TODO add streaming chat test here, consider converting to python so
# we can load all the messages while streaming

echo "💬 Testing chat endpoint..."
chat_status_code=$(curl -s -o chat_response.json -w "%{http_code}" \
    -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{
        "query": "Who is more likely to win between Federer and Nadal on clay court? Please just respond with a name and a single reason.",
        "player_a_id": "Roger Federer",
        "player_b_id": "Rafael Nadal",
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

cleanup_containers
