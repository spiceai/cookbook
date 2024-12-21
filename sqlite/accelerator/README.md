# SQLite Data Accelerator

Follow this recipe to configure dataset acceleration using SQLite.

_Tip: Open and refer to the [SQLite Data Accelerator](https://docs.spiceai.org/components/data-accelerators/sqlite) documentation while completing this recipe._

_Tip: Follow the [Advanced Data Refresh Recipe](../data-refresh/README.md) to learn more about advanced data refresh scenarios, such as programmatically updating `refresh_sql` and triggering data refreshes._

## Step 1. Initialize the Spice app

Ensure the Spice CLI is installed. If not, follow the Spice [Getting Started](https://docs.spiceai.org/getting-started) guide to install.

Clone the Spice samples repository and navigate to the `sqlite` directory:

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/sqlite/accelerator
```

Start the Spice runtime

```bash
spice run
```

Output:

```bash
2024-09-10T06:54:36.184935Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2024-09-10T06:54:36.185086Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2024-09-10T06:54:36.187305Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2024-09-10T06:54:36.193225Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2024-09-10T06:54:36.385124Z  INFO runtime: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2024-09-10T06:54:37.020990Z  INFO runtime: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), results cache enabled.
```

## Step 2. Run query against the dataset using the Spice SQL REPL

In a new terminal, start the Spice SQL REPL.

```bash
spice sql
```

Enter a query to display the longest taxi trips:

```sql
SELECT trip_distance, total_amount FROM taxi_trips ORDER BY trip_distance DESC LIMIT 10;
```

Output:

```bash
+---------------+--------------+
| trip_distance | total_amount |
+---------------+--------------+
| 312722.3      | 22.15        |
| 97793.92      | 36.31        |
| 82015.45      | 21.56        |
| 72975.97      | 20.04        |
| 71752.26      | 49.57        |
| 59282.45      | 33.52        |
| 59076.43      | 23.17        |
| 58298.51      | 18.63        |
| 51619.36      | 24.2         |
| 44018.64      | 52.43        |
+---------------+--------------+

Time: 2.1508365 seconds. 10 rows.
```

## Step3. Enable SQLite Accelerator

Use text editor to open `.spicepod.yaml` and uncomment `acceleration` section. Save.

Before:

```yaml
version: v1beta1
kind: Spicepod
name: spice_app
datasets:
  - from: s3://spiceai-demo-datasets/taxi_trips/2024/
    name: taxi_trips
    description: taxi trips in s3
    params:
      file_format: parquet
#   acceleration:
#     enabled: true
#     engine: sqlite
#     mode: file
```

After:

```yaml
version: v1beta1
kind: Spicepod
name: spice_app
datasets:
- from: s3://spiceai-demo-datasets/taxi_trips/2024/
  name: taxi_trips
  description: taxi trips in s3
  params:
    file_format: parquet
  acceleration:
    enabled: true
    engine: sqlite
    mode: file
```

The following output is shown in the Spice runtime terminal confirming new configuration is applied.

```bash
2024-09-10T06:59:21.908667Z  INFO runtime: Unloaded dataset taxi_trips
2024-09-10T06:59:22.524295Z  INFO runtime: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (sqlite:file), results cache enabled.
2024-09-10T06:59:22.525789Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2024-09-10T06:59:39.244473Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,964,624 rows (421.71 MiB) for dataset taxi_trips in 16s 718ms.
```

Run query to display the longest taxi trips again:

```sql
SELECT trip_distance, total_amount FROM taxi_trips ORDER BY trip_distance DESC LIMIT 10;
```

Output:

```bash
+---------------+--------------+
| trip_distance | total_amount |
+---------------+--------------+
| 312722.3      | 22.15        |
| 97793.92      | 36.31        |
| 82015.45      | 21.56        |
| 72975.97      | 20.04        |
| 71752.26      | 49.57        |
| 59282.45      | 33.52        |
| 59076.43      | 23.17        |
| 58298.51      | 18.63        |
| 51619.36      | 24.2         |
| 44018.64      | 52.43        |
+---------------+--------------+

Time: 0.193560667 seconds. 10 rows.
```

Observe query execution time decreased from **2.1508365** to **0.193560667** seconds.
