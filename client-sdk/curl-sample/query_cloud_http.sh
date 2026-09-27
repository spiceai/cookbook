#!/usr/bin/env bash
set -euo pipefail

curl -sS -X POST https://data.spiceai.io/v1/sql \
  -H "Content-Type: text/plain" \
  -H "X-API-Key: <YOUR_API_KEY>" \
  -d "SELECT * FROM <YOUR_DATASET> LIMIT 10"
echo
