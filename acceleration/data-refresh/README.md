# Advanced Data Refresh

Data refresh for accelerated datasets can be configured and tuned for specific scenarios.

Follow this recipe to dynamically refresh specific data at runtime by programmatically updating `refresh_sql` and triggering data refreshes.

_Tip: Open and refer to the [Refresh Data](https://docs.spiceai.org/components/data-accelerators/data-refresh) documentation while completing this recipe._

## Step 1. Initialize the Spice app

First ensure the Spice CLI is installed. If not, follow the Spice [Getting Started](https://docs.spiceai.org/getting-started) guide to install.

```bash
mkdir spice-data-refresh
cd spice-data-refresh

# Add the spiceai/quickstart Spicepod
spice add spiceai/quickstart

# Start the Spice runtime
spice run
```

The Spice runtime will start and the `taxi_trips` dataset included in the `spiceai/quickstart` Spicepod will be loaded.

```bash
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

**In a new terminal window**, run `spice sql` to start the Spice SQL REPL.

In the REPL, enter:

```sql
select avg(passenger_count) from taxi_trips;
```

Note the output is:

```bash
+---------------------------------+
| AVG(taxi_trips.passenger_count) |
+---------------------------------+
| 1.3392808966805005              |
+---------------------------------+
```

## Step 2. Filter the refresh data

In a code or text editor, open `spicepods/spiceai/quickstart/spicepod.yaml`.

In the `acceleration` section:

1. Add Refresh SQL below the `refresh_mode` setting to filter the dataset to a passenger_count of two.
2. Remove the line `refresh_check_interval: 10s` to prevent automated refreshes.

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
    refresh_mode: full
    refresh_sql: select * from taxi_trips where passenger_count = 2
```

Save the file and note that the dataset has been updated:

```console
2024-08-26T18:45:40.157775Z  INFO runtime: Updating accelerated dataset taxi_trips...
2024-08-26T18:45:40.619285Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2024-08-26T18:45:45.620097Z  INFO runtime::accelerated_table::refresh_task: Loaded 405,103 rows (54.93 MiB) for dataset taxi_trips in 5s.
2024-08-26T18:45:46.139435Z  INFO runtime: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (arrow), results cache enabled.
```

Swap to the Spice SQL REPL and enter:

```sql
select avg(passenger_count) from taxi_trips;
```

Note, the output is now:

```bash
+---------------------------------+
| AVG(taxi_trips.passenger_count) |
+---------------------------------+
| 2.0                             |
+---------------------------------+
```

The dataset was refreshed with data filtered to trips with a passenger count of 2.

## Step 3. Programmatically update the refresh SQL

In addition to editing the `spicepod.yaml` directly, the Refresh SQL can be updated by API.

Run the following cURL command to update it:

```bash
curl -i -X PATCH \
     -H "Content-Type: application/json" \
     -d '{
           "refresh_sql": "SELECT * FROM taxi_trips WHERE passenger_count = 3"
         }' \
     localhost:8090/v1/datasets/taxi_trips/acceleration
```

```bash
2024-08-26T18:49:50.591517Z  INFO runtime::accelerated_table: [refresh] Updated refresh SQL for taxi_trips to SELECT * FROM taxi_trips WHERE passenger_count = 3
```

The updated `refresh_sql` will be applied on the _next_ refresh (as determined by `refresh_check_interval`).

Make an additional call to trigger a refresh now:

```bash
curl -i -H "Content-Type: application/json" -X POST localhost:8090/v1/datasets/taxi_trips/acceleration/refresh --data "{}"
```

```bash
2024-08-26T18:50:32.364290Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2024-08-26T18:50:35.037819Z  INFO runtime::accelerated_table::refresh_task: Loaded 91,262 rows (12.43 MiB) for dataset taxi_trips in 2s 673ms.
```

Swap to the Spice SQL REPL and enter:

```sql
select avg(passenger_count) from taxi_trips;
```

Note, the output is now:

```bash
+---------------------------------+
| AVG(taxi_trips.passenger_count) |
+---------------------------------+
| 3.0                             |
+---------------------------------+
```

## Summary

This recipe demonstrated how to dynamically refresh specific data at runtime by updating the `refresh_sql` in `spicepod.yaml` and programmatically via API calls. This provides control over what data is queried and fetched from remote data sources and when it happens.
