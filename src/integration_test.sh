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
        docker compose down
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

echo "🎉 Integration test setup complete!"