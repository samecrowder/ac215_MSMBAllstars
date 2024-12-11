#!/bin/bash

# Function to check and start containers if needed
STARTED_CONTAINERS=0
setup_containers() {
    if [ "$(docker compose ps --status running | grep -c '')" -gt 1 ]; then
        echo "🔄 Reusing existing containers..."
        STARTED_CONTAINERS=0
    else
        echo "🧹 Cleaning up any existing containers..."
        docker compose down

        echo "🏗️ Building containers..."
        docker compose build

        echo "🚀 Starting services..."
        docker compose up -d
        STARTED_CONTAINERS=1
    fi
}

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

# Function to wait for all services
wait_for_all_services() {
    echo "🔍 Checking all services..."
    wait_for_service "api" 8000
    wait_for_service "probability_model" 8001
    wait_for_service "llm" 8002
    wait_for_service "ollama" 11434 "/api/tags"
}

# Function to cleanup based on whether we started new containers
# expects to be called after setup_containers is called
cleanup_containers() {
    if [ "$STARTED_CONTAINERS" = "1" ]; then
        echo "🧹 Cleaning up containers..."
        docker compose down
    else
        echo "🔄 Leaving existing containers running..."
    fi
}

setup_cache_directory() {
    echo "📁 Setting up GCS cache directory..."
    mkdir -p /tmp/gcs_cache
    chmod 777 /tmp/gcs_cache
}
