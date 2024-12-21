# Spice with gospice SDK

This recipe demonstrates how to use the gospice SDK to connect to a Spice runtime and query data.

## Prerequisites

This recipe requires [Go](https://go.dev/) to be installed.

## Start spice runtime

```shell
spice run
```

Output:

```shell
2024/11/27 16:24:27 INFO Checking for latest Spice runtime release...
2024/11/27 16:24:27 INFO Spice.ai runtime starting...
2024-11-28T00:24:28.411072Z  INFO runtime::init::dataset: Initializing dataset taxi_trips
2024-11-28T00:24:28.416797Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2024-11-28T00:24:28.416827Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2024-11-28T00:24:28.419672Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2024-11-28T00:24:28.421199Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2024-11-28T00:24:28.607738Z  INFO runtime::init::results_cache: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2024-11-28T00:24:29.247902Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (arrow), results cache enabled.
2024-11-28T00:24:29.249355Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2024-11-28T00:24:37.106088Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,964,624 rows (419.31 MiB) for dataset taxi_trips in 7s 856ms.
```

## Run sample application

```shell
go run .
```

Results:

```shell
go run .
VendorID: 2
tpep_pickup_datetime: 1705115889000000
fare_amount: 11.4
VendorID: 2
tpep_pickup_datetime: 1705117978000000
fare_amount: 13.5
VendorID: 2
tpep_pickup_datetime: 1705116362000000
fare_amount: 11.4
VendorID: 2
tpep_pickup_datetime: 1705118024000000
fare_amount: 27.5
VendorID: 2
tpep_pickup_datetime: 1705114708000000
fare_amount: 18.4
VendorID: 2
tpep_pickup_datetime: 1705118064000000
fare_amount: 14.2
VendorID: 2
tpep_pickup_datetime: 1705115215000000
fare_amount: 88.1
VendorID: 2
tpep_pickup_datetime: 1705116146000000
fare_amount: 10
VendorID: 2
tpep_pickup_datetime: 1705116079000000
fare_amount: 28.9
VendorID: 1
tpep_pickup_datetime: 1705115615000000
fare_amount: 35.2
```
