# SQLite Data Accelerator

Follow this recipe to configure dataset acceleration using SQLite.

_Tip: Open and refer to the [SQLite Data Accelerator](https://spiceai.org/docs/components/data-accelerators/sqlite) documentation while completing this recipe._

_Tip: Follow the [Advanced Data Refresh Recipe](../data-refresh/README.md) to learn more about advanced data refresh scenarios, such as programmatically updating `refresh_sql` and triggering data refreshes._

## Step 1. Initialize the Spice app

Ensure the Spice CLI is installed. If not, follow the Spice [Getting Started](https://spiceai.org/docs/getting-started) guide to install.

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

Startup logs vary by version and environment. Continue once `taxi_trips` is registered and the runtime is ready.

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

Use text editor to open `spicepod.yaml` and set `acceleration.enabled: true`. Save.

Before:

```yaml
version: v1
kind: Spicepod
name: spice_app
datasets:
  - from: s3://spiceai-demo-datasets/taxi_trips/2024/
    name: taxi_trips
    description: taxi trips in s3
    params:
      file_format: parquet
    acceleration:
      enabled: false
      engine: sqlite
      mode: file
```

After:

```yaml
version: v1
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

The exact refresh logs vary by version and environment. Continue when `taxi_trips` is re-registered with `acceleration (sqlite:file)` and refresh completes.

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
