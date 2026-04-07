# cURL Cloud Sample

Use [cURL](https://curl.se/) to run SQL against [Spice.ai Cloud](https://spice.ai) over HTTP.

## Links

- [cURL](https://curl.se/)
- [Spice.ai Cloud](https://spice.ai)
- [Spice.ai Cloud API documentation](https://docs.spiceai.org/api)

## Prerequisites

- [cURL](https://curl.se/)
- A Spice.ai Cloud API key
- A dataset available in your Cloud app

## Quick Start

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/client-sdk/curl-sample
```

Set your cloud values for the commands in this README:

```bash
export SPICE_API_KEY="your_api_key"
export SPICE_DATASET="your_dataset"
```

The script snippet keeps inline placeholders by design. Replace the API key and dataset placeholders in `query_cloud_http.sh`, then run:

```bash
bash query_cloud_http.sh
```

## Manual Query (HTTP)

```bash
curl -X POST https://data.spiceai.io/v1/sql \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${SPICE_API_KEY}" \
  -d "{\"query\": \"SELECT * FROM ${SPICE_DATASET} LIMIT 10\"}"
```

## Expected Result

You should receive JSON with query results in a `data` array.
