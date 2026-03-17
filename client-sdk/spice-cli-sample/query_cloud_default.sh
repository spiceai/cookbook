#!/usr/bin/env bash
set -euo pipefail

: "${SPICE_API_KEY:?Set SPICE_API_KEY before running this script.}"
SPICE_DATASET="${SPICE_DATASET:-my_dataset}"

spice sql --cloud --api-key "${SPICE_API_KEY}" \
  "SELECT * FROM ${SPICE_DATASET} LIMIT 10"