#!/bin/bash
# Start USD Search Service

set -e

echo "🚀 Starting USD Search Service..."

# Build the USD service container using repo.sh
echo "🔨 Building USD service container using repo.sh..."
./repo.sh package --container --name tonks-usd-search

  # Start the container
  echo "▶️ Starting USD service container..."
  docker run -d \
    --network usd-search-network \
    -p 8011:8011 \
    tonks-usd-search

echo "✅ USD Search Service started!"
echo "🌐 Service URL: http://localhost:8011"
echo "📚 API docs: http://localhost:8011/docs"
echo "🔍 Test search: curl 'http://localhost:8011/api/v1/search?q=chair'"
