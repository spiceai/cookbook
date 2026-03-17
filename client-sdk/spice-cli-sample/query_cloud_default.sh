#!/usr/bin/env bash
set -euo pipefail

spice sql --cloud --api-key "<YOUR_API_KEY>" \
  "SELECT * FROM <YOUR_DATASET> LIMIT 10"