# Cron-based Dataset Refresh

Spice supports specifying cron schedules for accelerated datasets, to refresh datasets on defined schedules.

Follow this recipe to schedule a dataset to refresh on a cron schedule.

_Tip: Open and refer to the [Data Refresh](https://spiceai.org/docs/features/data-acceleration/data-refresh) documentation while completing this recipe._

## Step 1. Initialize the Spice app

First ensure the Spice CLI is installed. If not, follow the Spice [Getting Started](https://docs.spiceai.org/getting-started) guide to install.

```bash
mkdir spice-cron-refresh
cd spice-cron-refresh

# Add the spiceai/quickstart Spicepod
spice add spiceai/quickstart

# Start the Spice runtime
spice run
```

The Spice Runtime will start and the `taxi_trips` dataset included in the `spiceai/quickstart` Spicepod will be loaded.

```console
Spice.ai runtime starting...
2024-08-26T18:43:28.915833Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2024-08-26T18:43:28.915869Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2024-08-26T18:43:28.915925Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2024-08-26T18:43:28.921589Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2024-08-26T18:43:29.115877Z  INFO runtime: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2024-08-26T18:43:29.636542Z  INFO runtime: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (arrow, 10s refresh), results cache enabled.
2024-08-26T18:43:29.637779Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2024-08-26T18:43:33.695650Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,964,624 rows (421.71 MiB) for dataset taxi_trips in 4s 57ms.
```

## Step 2. Configure a cron refresh schedule

Stop the Spice Runtime using `Ctrl-C`. In a code or text editor, open `spicepods/spiceai/quickstart/spicepod.yaml`.

In the `acceleration` section, add a `refresh_cron` parameter with a value of `*/30 * * * * *` to refresh every 30th second.

The `spicepod.yaml` should be as below:

```yaml
version: v1beta1
kind: Spicepod
name: quickstart

datasets:
- from: s3://spiceai-demo-datasets/taxi_trips/2024/
  name: taxi_trips
  description: taxi trips in s3
  params:
    file_format: parquet
  acceleration:
    enabled: true
    refresh_cron: "*/30 * * * * *"
```

Save the file, and restart the Spice runtime:

```bash
spice run
```

After the initial load, observe that the `taxi_trips` dataset refreshes on every 30th second:

```console
2025-06-09T06:27:32.836137Z  INFO runtime::init::caching: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2025-06-09T06:27:32.836265Z  INFO runtime::init::caching: Initialized search results cache;
2025-06-09T06:27:33.626524Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2025-06-09T06:27:33.626530Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-06-09T06:27:33.627071Z  INFO runtime::init::dataset: Initializing dataset taxi_trips
2025-06-09T06:27:33.630576Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-06-09T06:27:35.928527Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (arrow), results cache enabled.
2025-06-09T06:27:35.929924Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2025-06-09T06:27:50.915273Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,964,624 rows (399.41 MiB) for dataset taxi_trips in 14s 985ms.
2025-06-09T06:27:50.986350Z  INFO runtime: All components are loaded. Spice runtime is ready!
2025-06-09T06:28:00.001597Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2025-06-09T06:28:13.954105Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,964,624 rows (399.41 MiB) for dataset taxi_trips in 13s 952ms.
2025-06-09T06:28:30.001882Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2025-06-09T06:28:43.802372Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,964,624 rows (399.41 MiB) for dataset taxi_trips in 13s 800ms.
```