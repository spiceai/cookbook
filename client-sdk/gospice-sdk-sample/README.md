# Spice with gospice SDK

This recipe demonstrates how to use the gospice SDK to connect to a Spice runtime and query data.

Clone this cookbook repo locally and navigate to the `gospice-sdk-sample` directory:

```shell
git clone https://github.com/spiceai/cookbook.git
cd cookbook/client-sdk/gospice-sdk-sample/
```

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
go run main.go
```

Results:

```shell
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
