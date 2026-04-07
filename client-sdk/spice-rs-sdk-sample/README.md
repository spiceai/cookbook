# Spice with Rust SDK

Use the [Spice Rust SDK](https://crates.io/crates/spiceai) to query a local Spice runtime.

## Prerequisites

- [Rust](https://www.rust-lang.org/)
- [Spice CLI](https://docs.spiceai.org/getting-started)

## Quick Start

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/client-sdk/spice-rs-sdk-sample
```

Start Spice runtime in one terminal:

```bash
spice run
```

Sample runtime logs:

```text
2024/11/27 12:46:10 INFO Checking for latest Spice runtime release...
2024/11/27 12:46:10 INFO Spice.ai runtime starting...
2024-11-27T20:46:11.343825Z  INFO runtime::init::dataset: Initializing dataset taxi_trips
2024-11-27T20:46:11.346211Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2024-11-27T20:46:11.346574Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2024-11-27T20:46:11.346653Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2024-11-27T20:46:11.353386Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2024-11-27T20:46:11.544488Z  INFO runtime::init::results_cache: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2024-11-27T20:46:12.286180Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (arrow, 10s refresh), results cache enabled.
2024-11-27T20:46:12.287391Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2024-11-27T20:46:22.751704Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,964,624 rows (419.31 MiB) for dataset taxi_trips in 10s 464ms.
```

Run the Rust sample in another terminal:

```bash
cargo run
```

Sample output:

```text
=== Using query ===
VendorID: 2, tpep_pickup_datetime: 2024-01-06 14:41:17, fare_amount: 8.60
VendorID: 2, tpep_pickup_datetime: 2024-01-06 14:56:46, fare_amount: 7.20
VendorID: 2, tpep_pickup_datetime: 2024-01-06 14:28:42, fare_amount: 14.20
VendorID: 2, tpep_pickup_datetime: 2024-01-06 14:28:26, fare_amount: 37.30
VendorID: 2, tpep_pickup_datetime: 2024-01-06 14:35:06, fare_amount: 70.00
VendorID: 2, tpep_pickup_datetime: 2024-01-06 14:18:57, fare_amount: 19.10
VendorID: 2, tpep_pickup_datetime: 2024-01-06 14:40:11, fare_amount: 5.80
VendorID: 1, tpep_pickup_datetime: 2024-01-06 14:38:04, fare_amount: 12.10
VendorID: 2, tpep_pickup_datetime: 2024-01-06 14:14:22, fare_amount: 7.20
VendorID: 2, tpep_pickup_datetime: 2024-01-06 14:38:31, fare_amount: 7.90

=== Using query_with_params ===
VendorID: 2, tpep_pickup_datetime: 2024-01-26 06:56:06, fare_amount: 19.10
VendorID: 2, tpep_pickup_datetime: 2024-01-26 06:48:07, fare_amount: 70.00
VendorID: 1, tpep_pickup_datetime: 2024-01-26 06:29:55, fare_amount: 20.50
VendorID: 1, tpep_pickup_datetime: 2024-01-26 06:23:42, fare_amount: 10.70
VendorID: 2, tpep_pickup_datetime: 2024-01-26 06:08:06, fare_amount: 70.00
```

## Advanced

Build the sample without running it:

```bash
cargo build
```

## Links

- [Spice Rust SDK](https://github.com/spiceai/spice-rs)
- [crates.io](https://crates.io/crates/spiceai)
- [Spice.ai Cloud](https://spice.ai)
- [Spice.ai documentation](https://docs.spiceai.org)
