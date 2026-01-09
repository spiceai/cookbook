# Spice with spicepy SDK

This recipe demonstrates how to use the Spice Python SDK to connect to a Spice runtime and query data.

## Prerequisites

This recipe requires [uv](https://docs.astral.sh/uv/) to be installed.

- Install `uv` with:
  - macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

Navigate to `spicepy-sdk-sample`:

```shell
git clone https://github.com/spiceai/cookbook # skip if already cloned
cd cookbook/client-sdk/spicepy-sdk-sample
```

## Start spice runtime

```shell
spice run
```

```shell
2025/01/27 11:53:58 INFO Checking for latest Spice runtime release...
2025/01/27 11:54:01 INFO Spice.ai runtime starting...
2025-01-27T19:54:01.956890Z  INFO runtime::init::dataset: Initializing dataset taxi_trips
2025-01-27T19:54:01.957325Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-01-27T19:54:01.957341Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2025-01-27T19:54:01.958254Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-01-27T19:54:01.959596Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2025-01-27T19:54:02.157072Z  INFO runtime::init::results_cache: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2025-01-27T19:54:02.866819Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (arrow, 10s refresh), results cache enabled.
2025-01-27T19:54:02.868324Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2025-01-27T19:54:13.743056Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,964,624 rows (399.41 MiB) for dataset taxi_trips in 10s 874ms.
```

## Run sample application

```shell
uv run sample.py
```

Results:

```shell
➜ uv run sample.py 
=== Using query ===
VendorID: 1, tpep_pickup_datetime: 2024-01-11 09:37:05, fare_amount: 7.9
VendorID: 1, tpep_pickup_datetime: 2024-01-11 09:50:21, fare_amount: 8.6
VendorID: 1, tpep_pickup_datetime: 2024-01-11 09:59:34, fare_amount: 5.1
VendorID: 2, tpep_pickup_datetime: 2024-01-11 09:05:47, fare_amount: 23.3
VendorID: 1, tpep_pickup_datetime: 2024-01-11 09:52:47, fare_amount: 6.5
VendorID: 2, tpep_pickup_datetime: 2024-01-11 09:37:26, fare_amount: 24.0
VendorID: 2, tpep_pickup_datetime: 2024-01-11 09:10:05, fare_amount: 33.8
VendorID: 2, tpep_pickup_datetime: 2024-01-11 09:03:54, fare_amount: 6.5
VendorID: 1, tpep_pickup_datetime: 2024-01-11 09:14:08, fare_amount: 20.5
VendorID: 1, tpep_pickup_datetime: 2024-01-11 09:58:26, fare_amount: 19.5

=== Using query with params ===
VendorID: 2, tpep_pickup_datetime: 2024-01-25 22:33:48, fare_amount: 19.8
VendorID: 2, tpep_pickup_datetime: 2024-01-25 22:55:27, fare_amount: 17.0
VendorID: 2, tpep_pickup_datetime: 2024-01-25 22:14:50, fare_amount: 31.0
VendorID: 2, tpep_pickup_datetime: 2024-01-25 22:52:11, fare_amount: 21.9
VendorID: 1, tpep_pickup_datetime: 2024-01-25 22:06:02, fare_amount: 13.5
```
