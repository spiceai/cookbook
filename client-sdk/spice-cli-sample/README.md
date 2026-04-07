# Spice CLI Cloud Sample

Use the [Spice CLI](https://docs.spiceai.org/getting-started) to run SQL against [Spice.ai Cloud](https://spice.ai).

## Links

- [Spice CLI documentation](https://docs.spiceai.org/cli)
- [Spice CLI installation](https://docs.spiceai.org/getting-started)
- [Spice.ai Cloud](https://spice.ai)
- [Spice OSS GitHub](https://github.com/spiceai/spiceai)

## Prerequisites

- [Spice CLI](https://docs.spiceai.org/getting-started)
- A Spice.ai Cloud API key
- A dataset available in your Cloud app

Install Spice CLI if needed:

```bash
curl https://install.spiceai.org | /bin/bash
```

## Quick Start

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/client-sdk/spice-cli-sample
```

Set your cloud values for the commands in this README:

```bash
export SPICE_API_KEY="your_api_key"
export SPICE_DATASET="your_dataset"
```

The script snippets keep inline placeholders by design. Replace the API key and dataset placeholders in the scripts, then run:

```bash
bash query_cloud_default.sh
```

## Additional URL Examples

Run with an explicit gRPC endpoint URL:

```bash
bash query_cloud_grpc.sh
```

Run with an explicit HTTP endpoint URL:

```bash
bash query_cloud_http.sh
```

## Manual Commands

```bash
spice sql \
  --cloud \
  --api-key "${SPICE_API_KEY}" \
  "SELECT * FROM ${SPICE_DATASET} LIMIT 10"

spice sql \
  --api-key "${SPICE_API_KEY}" \
  --endpoint "grpc+tls://flight.spiceai.io:443" \
  "SELECT * FROM ${SPICE_DATASET} LIMIT 10"

spice sql \
  --api-key "${SPICE_API_KEY}" \
  --endpoint "https://data.spiceai.io" \
  "SELECT * FROM ${SPICE_DATASET} LIMIT 10"
```
