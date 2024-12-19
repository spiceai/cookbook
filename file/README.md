# File Data Connector Recipe

Follow these steps to get started with using local files as a Data Connector.

## Parquet

1. Download or move a parquet file locally

  ```shell
  wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet -O yellow_tripdata_2024-01.parquet
  ```

2. Create the Spicepod.

  ```shell
  cat <<EOF > spicepod.yaml
  version: v1beta1
  kind: Spicepod
  name: file_recipe
  datasets:
    - name: yellow_taxis
      from: file://yellow_tripdata_2024-01.parquet
  EOF
  ```

3. Run Spice runtime

  ```shell
  spice run
  ```

4. Run SQL query

In a new terminal, run the following SQL query using `spice sql`

```sql
select avg(passenger_count) from yellow_taxis;
```

```output
sql> select avg(passenger_count) from yellow_taxis;
+-----------------------------------+
| avg(yellow_taxis.passenger_count) |
+-----------------------------------+
| 1.3392808966805005                |
+-----------------------------------+

Time: 0.0253585 seconds. 1 rows.
```

5. (Optional) Cleanup

  ```shell
  rm spicepod.yaml
  ```

## Documents

1. Download markdown documents

  ```shell
  base_url="https://raw.githubusercontent.com/spiceai/docs/refs/heads/trunk/spiceaidocs/docs/components/data-connectors"

  files=(
    "clickhouse.md"
    "databricks.md"
    "debezium.md"
    "delta-lake.md"
  )

  for file in "${files[@]}"; do
    wget "$base_url/$file"
  done
  ```

2. Create the Spicepod.

  ```shell
  cat <<EOF > spicepod.yaml
  version: v1beta1
  kind: Spicepod
  name: file_recipe
  datasets:
    - name: docs
      from: file:./
      params:
        file_format: md
  EOF
  ```

3. Run Spice runtime

  ```shell
  spice run
  ```

4. Run SQL query

  In a new terminal, run the following SQL query using `spice sql`

  ```sql
  select location from docs;
  ```
