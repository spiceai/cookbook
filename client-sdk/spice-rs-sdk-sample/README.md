# Spice with Rust SDK Recipe

This recipe demonstrates how to use the Spice Rust SDK to connect to a Spice runtime and query data.

## Prerequisites

This recipe requires [Rust](https://www.rust-lang.org/) to be installed.

## Start spice runtime

```shell
spice run
```

```shell
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

## Build sample application

```shell
cargo build
```

## Run sample application

```shell
cargo run
```

Results:

```shell
cargo run
    Finished dev [unoptimized + debuginfo] target(s) in 0.23s
     Running `target/debug/spice-rs-sdk-sample`
RecordBatch { schema: Schema { fields: [Field { name: "VendorID", data_type: Int32, nullable: true, dict_id: 0, dict_is_ordered: false, metadata: {} }, Field { name: "tpep_pickup_datetime", data_type: Timestamp(Microsecond, None), nullable: true, dict_id: 0, dict_is_ordered: false, metadata: {} }, Field { name: "fare_amount", data_type: Float64, nullable: true, dict_id: 0, dict_is_ordered: false, metadata: {} }], metadata: {} }, columns: [PrimitiveArray<Int32>
[
  2,
  2,
  2,
  2,
  2,
  1,
  2,
  2,
  2,
  1,
], PrimitiveArray<Timestamp(Microsecond, None)>
[
  2024-01-24T15:17:12,
  2024-01-24T15:52:24,
  2024-01-24T15:08:55,
  2024-01-24T15:42:55,
  2024-01-24T15:52:23,
  2024-01-24T15:30:55,
  2024-01-24T15:21:48,
  2024-01-24T15:47:59,
  2024-01-24T15:55:32,
  2024-01-24T15:02:22,
], PrimitiveArray<Float64>
[
  20.5,
  10.7,
  25.4,
  9.3,
  18.4,
  70.0,
  40.8,
  35.2,
  36.6,
  11.4,
]], row_count: 10 }
```
