#!/bin/bash

# Exit on any error
set -e

echo "🧹 Cleaning up any existing containers..."
docker compose down

echo "🏗️ Building containers..."
docker compose build

echo "🚀 Starting services..."
# Disable web service for integration tests
docker compose up -d --scale web=0

echo "⏳ Waiting for API to be ready..."
timeout=300  # 5 minutes in seconds
interval=5   # Check every 5 seconds
elapsed=0

while true; do
    if [ $elapsed -ge $timeout ]; then
        echo "❌ Timeout waiting for API to be ready"
        echo "📝 Last API response:"
        curl -s http://localhost:8000/health || echo "Failed to get response"
        echo -e "\n📋 Last 10 lines of container logs:"
        echo -e "\n🔍 API logs:"
        docker compose logs --tail=10 api
        echo -e "\n🔍 LLM logs:"
        docker compose logs --tail=10 llm
        echo -e "\n🔍 Probability Model logs:"
        docker compose logs --tail=10 probability_model
        exit 1
    fi

    status_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo "failed")
    
    if [ "$status_code" = "200" ]; then
        echo "✅ API is ready!"
        break
    fi

    echo "⏳ Still waiting for API... (${elapsed}s elapsed)"
    if [ "$status_code" != "failed" ]; then
        echo "📝 API Response (Status: $status_code):"
        curl -s http://localhost:8000/health || echo "Failed to get response"
        echo -e "\n📋 Last 10 lines of container logs:"
        echo -e "\n🔍 API logs:"
        docker compose logs --tail=10 api
        echo -e "\n🔍 LLM logs:"
        docker compose logs --tail=10 llm
        echo -e "\n🔍 Probability Model logs:"
        docker compose logs --tail=10 probability_model
    fi
    
    sleep $interval
    elapsed=$((elapsed + interval))
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

# TODO add streaming chat test here, consider converting to python so 
# we can load all the messages while streaming

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
