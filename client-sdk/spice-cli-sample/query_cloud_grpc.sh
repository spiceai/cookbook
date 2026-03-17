#!/usr/bin/env bash
set -euo pipefail

spice sql \
  --api-key "<YOUR_API_KEY>" \
  --endpoint "grpc+tls://flight.spiceai.io:443" \
  "SELECT * FROM <YOUR_DATASET> LIMIT 10"
