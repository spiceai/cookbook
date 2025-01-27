# Spice with spicepy SDK

This recipe demonstrates how to use the Spice Python SDK to connect to a Spice runtime and query data.

## Prerequisites

This recipe requires [Python](https://www.python.org/) to be installed.

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

## Install dependencies

```shell
python -m venv .venv
source .venv/bin/activate
pip install git+https://github.com/spiceai/spicepy@v3.0.0
```

## Run sample application

```shell
python sample.py
```

Results:

```shell
➜ python sample.py 
   trip_distance  total_amount
0      312722.30         22.15
1       97793.92         36.31
2       82015.45         21.56
3       72975.97         20.04
4       71752.26         49.57
5       59282.45         33.52
6       59076.43         23.17
7       58298.51         18.63
8       51619.36         24.20
9       44018.64         52.43
```
