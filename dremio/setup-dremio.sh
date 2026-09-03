#!/usr/bin/env bash
# Bootstraps the local Dremio instance started by docker-compose:
#   1. Creates the first (admin) user
#   2. Adds /opt/dremio/datasets (the cookbook `data` directory) as a NAS source named `datasets`
#   3. Promotes the taxi_trips folder to the physical dataset `datasets.taxi_trips`
#
# Safe to re-run: steps that are already done are skipped.
set -euo pipefail

DREMIO_URL="${DREMIO_URL:-http://localhost:9047}"
DREMIO_USER="${DREMIO_USER:-demo}"
DREMIO_PASSWORD="${DREMIO_PASSWORD:-demo1234}"

# Reads the first value of a top-level JSON string field from stdin.
json_field() {
  grep -o "\"$1\":\"[^\"]*\"" | head -1 | cut -d'"' -f4
}

echo "Waiting for Dremio at ${DREMIO_URL} (first start takes 1-2 minutes)..."
for _ in $(seq 1 150); do
  if curl -sf -o /dev/null "${DREMIO_URL}/apiv2/server_status"; then break; fi
  sleep 2
done
curl -sf -o /dev/null "${DREMIO_URL}/apiv2/server_status" || {
  echo "Dremio did not become ready. Check 'docker compose logs dremio'." >&2
  exit 1
}

echo "Creating the first user '${DREMIO_USER}'..."
curl -s -o /dev/null -X PUT "${DREMIO_URL}/apiv2/bootstrap/firstuser" \
  -H 'Authorization: _dremionull' \
  -H 'Content-Type: application/json' \
  -d "{\"userName\":\"${DREMIO_USER}\",\"firstName\":\"Demo\",\"lastName\":\"User\",\"email\":\"${DREMIO_USER}@example.com\",\"createdAt\":1526186430755,\"password\":\"${DREMIO_PASSWORD}\"}"

TOKEN=$(curl -s -X POST "${DREMIO_URL}/apiv2/login" \
  -H 'Content-Type: application/json' \
  -d "{\"userName\":\"${DREMIO_USER}\",\"password\":\"${DREMIO_PASSWORD}\"}" | json_field token)

if [ -z "${TOKEN}" ]; then
  echo "Could not log in to Dremio as '${DREMIO_USER}'." >&2
  exit 1
fi
AUTH="Authorization: _dremio${TOKEN}"

echo "Adding the 'datasets' NAS source..."
curl -s -o /dev/null -X POST "${DREMIO_URL}/api/v3/catalog" \
  -H "${AUTH}" -H 'Content-Type: application/json' \
  -d '{"entityType":"source","name":"datasets","type":"NAS","config":{"path":"/opt/dremio/datasets"}}'

echo "Promoting datasets.taxi_trips to a physical dataset..."
ENTITY=$(curl -s "${DREMIO_URL}/api/v3/catalog/by-path/datasets/taxi_trips" -H "${AUTH}")
ENTITY_TYPE=$(printf '%s' "${ENTITY}" | json_field entityType)
FOLDER_ID=$(printf '%s' "${ENTITY}" | json_field id)

if [ "${ENTITY_TYPE}" = "dataset" ]; then
  echo "  already promoted"
elif [ "${ENTITY_TYPE}" = "folder" ] && [ -n "${FOLDER_ID}" ]; then
  ENCODED_ID=$(printf '%s' "${FOLDER_ID}" | sed 's|:|%3A|g; s|/|%2F|g')
  RESULT=$(curl -s -X POST "${DREMIO_URL}/api/v3/catalog/${ENCODED_ID}" \
    -H "${AUTH}" -H 'Content-Type: application/json' \
    -d "{\"entityType\":\"dataset\",\"id\":\"${FOLDER_ID}\",\"path\":[\"datasets\",\"taxi_trips\"],\"type\":\"PHYSICAL_DATASET\",\"format\":{\"type\":\"Parquet\"}}")
  if printf '%s' "${RESULT}" | grep -q '"errorMessage"'; then
    echo "Failed to promote datasets.taxi_trips: ${RESULT}" >&2
    exit 1
  fi
else
  echo "Could not find datasets.taxi_trips - is the ../data directory mounted?" >&2
  echo "  response: ${ENTITY}" >&2
  exit 1
fi

echo
echo "Dremio is ready:"
echo "  UI:           ${DREMIO_URL} (${DREMIO_USER} / ${DREMIO_PASSWORD})"
echo "  Arrow Flight: grpc://localhost:32010"
echo "  Dataset:      datasets.taxi_trips"
