# cURL Cloud Sample

Use cURL to run SQL against Spice.ai Cloud over HTTP.

## Prerequisites

- [cURL](https://curl.se/)
- A Spice.ai Cloud API key
- A dataset available in your Cloud app

## Quick Start

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/client-sdk/curl-sample

export SPICE_API_KEY="<your-api-key>"
export SPICE_DATASET="my_dataset"

bash query_cloud_http.sh
```

## Manual Query (HTTP)

```bash
curl -X POST https://data.spiceai.io/v1/sql \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${SPICE_API_KEY}" \
  -d "{\"query\": \"SELECT * FROM ${SPICE_DATASET:-my_dataset} LIMIT 10\"}"
```

## Expected Result

You should receive JSON with query results in a `data` array.
