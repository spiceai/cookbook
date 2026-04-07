#!/usr/bin/env bash
set -euo pipefail

curl -sS -X POST https://data.spiceai.io/v1/sql \
  -H "Content-Type: application/json" \
  -H "X-API-Key: \"<YOUR_API_KEY>\"" \
  -d "{\"query\": \"SELECT * FROM <YOUR_DATASET> LIMIT 10\"}"
echo
