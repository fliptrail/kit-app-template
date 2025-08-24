#!/bin/bash
# Setup ZincSearch with USD data

set -e

echo "🔧 Setting up ZincSearch with USD data..."

# Step 2: Start ZincSearch container (based on official docs)
echo "🚀 Starting ZincSearch container..."

echo "Creating a docker network for ZincSearch..."
docker network create usd-search-network

docker run -d \
  --name zincsearch \
  --network usd-search-network \
  -p 4080:4080 \
  -e ZINC_DATA_PATH="/data" \
  -e ZINC_FIRST_ADMIN_USER=admin \
  -e ZINC_FIRST_ADMIN_PASSWORD=Complexpass#123 \
  public.ecr.aws/zinclabs/zincsearch:latest

# Step 3: Wait for ZincSearch to be ready
echo "⏳ Waiting for ZincSearch to start..."
sleep 10

for i in {1..30}; do
  if curl -s http://localhost:4080/api/index >/dev/null 2>&1; then
    echo "✅ ZincSearch is ready!"
    break
  fi
  echo "Waiting... ($i/30)"
  sleep 2
done

# Step 4: Create index and load CSV data
echo "📝 Creating index and loading CSV data..."

# Create index
curl -X PUT "http://localhost:4080/api/index" \
  -H "Content-Type: application/json" \
  -u admin:Complexpass#123 \
  -d '{
    "name": "usd_assets",
    "storage_type": "disk",
    "mappings": {
      "properties": {
        "path": {"type": "text", "index": true, "store": true},
        "filename": {"type": "text", "index": true, "store": true},
        "directory": {"type": "text", "index": true, "store": true},
        "bucket": {"type": "keyword", "index": true, "store": true},
        "size": {"type": "numeric", "index": true, "store": true},
        "keywords": {"type": "text", "index": true, "store": true}
      }
    }
  }'

# Convert CSV to NDJSON and load
echo "📥 Converting CSV to NDJSON and loading into ZincSearch..."
python -c "
import csv
import json

with open('usd_assets_cache.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    with open('usd_assets.ndjson', 'w') as jsonfile:
        for row in reader:
            # Convert size to int
            try:
                row['size'] = int(row['size'])
            except:
                row['size'] = 0

            # Create zinc bulkv2 format
            jsonfile.write(json.dumps(row) + '\n')
"

# Load the NDJSON file using bulkv2
# Create a properly formatted bulk request file
echo "Creating bulk request file..."
echo '{"index":"usd_assets","records":[' > bulk_request.json
cat usd_assets.ndjson | sed 's/$/,/' | sed '$ s/,$//' >> bulk_request.json
echo ']}' >> bulk_request.json

curl -X POST "http://localhost:4080/api/_bulkv2" \
  -H "Content-Type: application/json" \
  -u admin:Complexpass#123 \
  --data-binary @bulk_request.json

# Clean up temporary file
rm bulk_request.json

echo "✅ ZincSearch setup complete!"
echo "🌐 ZincSearch UI: http://localhost:4080"
echo "📊 Test search: curl 'http://localhost:4080/api/usd_assets/_search' -u admin:Complexpass#123 -d '{\"search_type\":\"match\",\"query\":{\"term\":\"chair\"},\"max_results\":10}'"
