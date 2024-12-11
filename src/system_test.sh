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
timeout=300  # 5 minutes in seconds
interval=5   # Check every 5 seconds
elapsed=0

while true; do
    if [ $elapsed -ge $timeout ]; then
        echo "❌ Timeout waiting for API to be ready"
        echo "📝 Last API response:"
        curl -s http://localhost:8000/health || echo "Failed to get response"
        echo -e "\n📋 Container logs:"
        docker compose logs
        exit 1
    fi

    status_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo "failed")
    
    if [ "$status_code" = "200" ]; then
        sleep 180 # wait for other services to be ready
        echo "✅ API is ready!"
        break
    fi

    echo "⏳ Still waiting for API... (${elapsed}s elapsed)"
    sleep $interval
    elapsed=$((elapsed + interval))
done

echo "🎭 Running Playwright E2E tests..."
cd frontend/tennis-app
npx playwright install --with-deps chromium
npm run test:e2e

echo "🎉 All system tests passed successfully!"
cd ../..
docker compose down 