#!/bin/bash

# Exit on any error
set -e

# Add flag to track if we started new containers
CONTAINERS_STARTED=false

# Function to wait for a service to be healthy
wait_for_service() {
    local service_name=$1
    local port=$2
    local health_path=${3:-"/health"} # Default to /health, but allow override
    local timeout=300                 # 5 minutes in seconds
    local interval=5                  # Check every 5 seconds
    local elapsed=0

    echo "⏳ Waiting for $service_name to be ready..."

    while true; do
        if [ $elapsed -ge $timeout ]; then
            echo "❌ Timeout waiting for $service_name to be ready"
            echo "📝 Last response:"
            curl -s "http://localhost:$port$health_path" || echo "Failed to get response"
            echo -e "\n📋 Container logs:"
            docker compose logs $service_name
            exit 1
        fi

        # run curl, get the http status code
        set +e
        status_code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port$health_path" 2>/dev/null)
        set -e

        if [ "$status_code" = "200" ]; then
            echo "✅ $service_name is ready!"
            break
        fi

        echo "⏳ Still waiting for $service_name... (${elapsed}s elapsed)"
        if [ "$status_code" != "000" ]; then
            echo "📝 Response (Status: $status_code)"
        else
            echo "📝 Service not reachable yet"
        fi

        sleep $interval
        elapsed=$((elapsed + interval))
    done
}

# Check if containers are already running
if [ "$(docker compose ps --status running | grep -c '')" -gt 1 ]; then
    echo "🔄 Reusing existing containers..."
else
    echo "🧹 Cleaning up any existing containers..."
    docker compose down

    echo "🏗️ Building containers..."
    docker compose build

    echo "🚀 Starting services..."
    docker compose up -d
    CONTAINERS_STARTED=true
fi

# Wait for all services to be ready
echo "🔍 Checking all services..."
wait_for_service "api" 8000
wait_for_service "probability_model" 8001
wait_for_service "llm" 8002
wait_for_service "ollama" 11434 "/api/tags"

echo "🎭 Running Playwright E2E tests..."
cd frontend/tennis-app
npx playwright install --with-deps chromium

# even if this fails, we should still shut down the containers
set +e
npm run test:e2e
test_result=$?
set -e

if [ $test_result -eq 0 ]; then
    echo "🎉 All system tests passed successfully!"
else
    echo "❌ Some system tests failed"
fi
cd ../..

# Only shut down if we started the containers
if [ "$CONTAINERS_STARTED" = true ]; then
    echo "🧹 Cleaning up containers..."
    docker compose down
else
    echo "🔄 Leaving existing containers running..."
fi

exit $test_result
