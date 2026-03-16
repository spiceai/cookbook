# Spice CLI Cloud Sample

Sample scripts for connecting to your Spice Cloud app using the [Spice CLI](https://docs.spiceai.org/getting-started).

## Prerequisites

Install the Spice CLI:

```bash
curl https://install.spiceai.org | /bin/bash
```

## Usage

### Query via gRPC (Arrow Flight)

```bash
spice sql --api-key <YOUR_API_KEY> --flight-url flight.spiceai.io:443 \
  "SELECT * FROM my_dataset LIMIT 10"
```

### Query via HTTP

```bash
spice sql --api-key <YOUR_API_KEY> --http-url https://data.spiceai.io \
  "SELECT * FROM my_dataset LIMIT 10"
```
