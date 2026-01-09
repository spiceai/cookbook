# Spice with Dotnet SDK

This recipe shows how to interact with Spice using the [Dotnet SDK](https://github.com/spiceai/spice-dotnet).

## Prerequisites

-   [Spice](https://github.com/spiceai/spiceai) is installed
-   [Dotnet](https://dotnet.microsoft.com/en-us/download)

## Clone this sample

```shell
git clone https://github.com/spiceai/cookbook.git
cd cookbook/client-sdk/spice-dotnet-sdk-sample
```

## Start the Spice runtime

```shell
spice run
```

```shell
2025-08-28T21:08:10.674387Z  INFO spiced: Starting runtime v1.7.0-unstable-build.246c46c4d-dev+models
2025-08-28T21:08:10.675513Z  INFO runtime::init::caching: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2025-08-28T21:08:10.675671Z  INFO runtime::init::caching: Initialized search results cache;
2025-08-28T21:08:11.148956Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-08-28T21:08:11.149031Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2025-08-28T21:08:11.151175Z  INFO runtime::init::dataset: Dataset taxi_trips initializing...
2025-08-28T21:08:11.162604Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-08-28T21:08:12.336410Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (arrow, 10s refresh), results cache enabled.
2025-08-28T21:08:12.338066Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2025-08-28T21:08:20.383434Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,964,624 rows (399.41 MiB) for dataset taxi_trips in 8s 45ms.
2025-08-28T21:08:20.455383Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

## Run the sample

```shell
dotnet run
```

```shell
=== Using Query ===
VendorID: 2, tpep_pickup_datetime: 2024-01-09 23:22:13, fare_amount: 7.20
VendorID: 1, tpep_pickup_datetime: 2024-01-09 23:40:08, fare_amount: 18.40
VendorID: 2, tpep_pickup_datetime: 2024-01-09 23:01:47, fare_amount: 15.60
VendorID: 2, tpep_pickup_datetime: 2024-01-09 23:26:58, fare_amount: 10.00
VendorID: 2, tpep_pickup_datetime: 2024-01-09 23:32:38, fare_amount: 70.00
VendorID: 2, tpep_pickup_datetime: 2024-01-09 23:01:50, fare_amount: 14.20
VendorID: 2, tpep_pickup_datetime: 2024-01-09 23:44:50, fare_amount: 7.20
VendorID: 1, tpep_pickup_datetime: 2024-01-09 23:32:11, fare_amount: 16.30
VendorID: 2, tpep_pickup_datetime: 2024-01-09 23:47:12, fare_amount: 10.70
VendorID: 2, tpep_pickup_datetime: 2024-01-09 23:35:00, fare_amount: 14.20

=== Using Query with Parameters ===
VendorID: 2, tpep_pickup_datetime: 2024-01-31 09:54:36, fare_amount: 7.20
VendorID: 2, tpep_pickup_datetime: 2024-01-31 09:04:39, fare_amount: 44.30
VendorID: 2, tpep_pickup_datetime: 2024-01-31 09:12:53, fare_amount: 7.90
VendorID: 2, tpep_pickup_datetime: 2024-01-31 09:24:15, fare_amount: 27.50
VendorID: 2, tpep_pickup_datetime: 2024-01-31 09:42:13, fare_amount: 7.90
```
