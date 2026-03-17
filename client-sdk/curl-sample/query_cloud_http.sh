#!/usr/bin/env bash
set -euo pipefail

: "${SPICE_API_KEY:?Set SPICE_API_KEY before running this script.}"
SPICE_DATASET="${SPICE_DATASET:-my_dataset}"

curl -sS -X POST https://data.spiceai.io/v1/sql \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${SPICE_API_KEY}" \
  -d "{\"query\": \"SELECT * FROM ${SPICE_DATASET} LIMIT 10\"}"
echo
