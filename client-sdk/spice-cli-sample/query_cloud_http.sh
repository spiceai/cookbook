#!/usr/bin/env bash
set -euo pipefail

spice sql \
  --api-key \""<YOUR_API_KEY>\"" \
  --endpoint "https://data.spiceai.io" \
  "SELECT * FROM <YOUR_DATASET> LIMIT 10"
