#!/bin/bash

# Exit on any error
set -e

# Source common functions
source "$(dirname "$0")/test_utils.sh"

setup_cache_directory
setup_containers

# Wait for all services
wait_for_all_services

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

cleanup_containers

exit $test_result
