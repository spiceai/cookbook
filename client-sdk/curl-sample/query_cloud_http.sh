# Query via HTTP API
curl -X POST https://data.spiceai.io/v1/sql \
  -H "Content-Type: application/json" \
  -H "X-API-Key: API_KEY" \
  -d '{"query": "SELECT * FROM my_dataset LIMIT 10"}'
