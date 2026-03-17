#!/usr/bin/env bash
set -euo pipefail

: "${SPICE_API_KEY:?Set SPICE_API_KEY before running this script.}"
SPICE_ENDPOINT="${SPICE_ENDPOINT:-https://data.spiceai.io}"
SPICE_DATASET="${SPICE_DATASET:-my_dataset}"

spice sql --api-key "${SPICE_API_KEY}" --endpoint "${SPICE_ENDPOINT}" \
  "SELECT * FROM ${SPICE_DATASET} LIMIT 10"
