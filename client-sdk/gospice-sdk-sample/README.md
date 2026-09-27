# Spice with gospice SDK

Works with `v1.0+`

Use the [gospice SDK](https://github.com/spiceai/gospice) to query Spice from Go.

## What This Sample Includes

- `main.go`: Query a local Spice runtime, including a parameterized query.
- `cloud/main.go`: Query Spice.ai Cloud with inline replacement values.

## Prerequisites

- [Go](https://go.dev/) 1.25+
- [Spice CLI](https://docs.spiceai.org/getting-started) for local mode

## Local Quick Start

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/client-sdk/gospice-sdk-sample
```

Start Spice runtime in one terminal:

```bash
spice run
```

Sample runtime logs:

```text
 INFO Spice.ai runtime starting...
2024-11-28T00:24:28.411072Z  INFO runtime::init::dataset: Dataset taxi_trips initializing...
2024-11-28T00:24:28.416797Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2024-11-28T00:24:28.419672Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2024-11-28T00:24:28.607738Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2024-11-28T00:24:29.247902Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (arrow), results cache enabled.
2024-11-28T00:24:29.249355Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset taxi_trips
2024-11-28T00:24:37.106088Z  INFO runtime_table::accelerated::refresh_task: Loaded 2,964,624 rows (399.38 MiB) for dataset taxi_trips in 7s 856ms.
```

Run the Go sample in another terminal:

```bash
go run main.go
```

Sample output:

```text
=== Using Sql ===
VendorID: 2, tpep_pickup_datetime: 1706465757000000, fare_amount: 15.6
VendorID: 2, tpep_pickup_datetime: 1706466833000000, fare_amount: 14.2
VendorID: 2, tpep_pickup_datetime: 1706465786000000, fare_amount: 7.9
VendorID: 1, tpep_pickup_datetime: 1706464867000000, fare_amount: 14.2
VendorID: 1, tpep_pickup_datetime: 1706466244000000, fare_amount: 15.6
VendorID: 1, tpep_pickup_datetime: 1706467652000000, fare_amount: 33.1
VendorID: 1, tpep_pickup_datetime: 1706465767000000, fare_amount: 7.2
VendorID: 1, tpep_pickup_datetime: 1706466975000000, fare_amount: 46.4
VendorID: 1, tpep_pickup_datetime: 1706464846000000, fare_amount: 17
VendorID: 1, tpep_pickup_datetime: 1706467147000000, fare_amount: 9.3

=== Using SqlWithParams ===
VendorID: 2, tpep_pickup_datetime: 1706252166000000, fare_amount: 19.1
VendorID: 2, tpep_pickup_datetime: 1706251687000000, fare_amount: 70
VendorID: 1, tpep_pickup_datetime: 1706250595000000, fare_amount: 20.5
VendorID: 1, tpep_pickup_datetime: 1706250222000000, fare_amount: 10.7
VendorID: 2, tpep_pickup_datetime: 1706249286000000, fare_amount: 70
```

## Spice.ai Cloud Quick Start

Set your API key for the commands in this README:

```bash
export SPICE_API_KEY="your_api_key"
```

The cloud snippet keeps an inline API key placeholder by design. Replace the API key placeholder in `cloud/main.go` with `${SPICE_API_KEY}`, then run:

```bash
go run ./cloud
```

Expected output is a list of tables from `show tables;`.

## Links

- [gospice SDK](https://github.com/spiceai/gospice)
- [Go package](https://pkg.go.dev/github.com/spiceai/gospice/v8)
- [Spice.ai Cloud](https://spice.ai)
- [Spice.ai documentation](https://docs.spiceai.org)
