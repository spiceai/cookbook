# File Data Connector Recipe

Using the [File Data Connector](https://spiceai.org/docs/components/data-connectors/file), you can create datasets from files. This enables you to easily query locally accessible data stored in various file formats, including CSV, Parquet, and Markdown.

## Prerequisites

- Spice.ai CLI installed (see [Getting Started](https://docs.spiceai.org/getting-started))

## Query Parquet Files

Follow these steps to use local Parquet files as a dataset.

### Step 1: Download or Move a Parquet File Locally

Download a sample Parquet file using the following command:

```shell
curl https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet -o yellow_tripdata_2024-01.parquet
```

### Step 2: Create the Spicepod

```shell
cat <<EOF > spicepod.yaml
version: v1
kind: Spicepod
name: file_recipe
datasets:
  - name: yellow_taxis
    from: file://yellow_tripdata_2024-01.parquet
EOF
```

### Step 3: Start the Spice Runtime

Run the Spice runtime to load the dataset:

```shell
spice run
```

### Step 4: Query the Dataset Using SQL

Open a new terminal and start the SQL REPL:

```shell
spice sql
```

Then execute a query on the `yellow_taxis` dataset.

```sql
select avg(passenger_count) from yellow_taxis;
```

You should see the following output:

```output
sql> select avg(passenger_count) from yellow_taxis;
+-----------------------------------+
| avg(yellow_taxis.passenger_count) |
+-----------------------------------+
| 1.3392808966805005                |
+-----------------------------------+

Time: 0.0253585 seconds. 1 rows.
```

### Step 5: Terminate the Spice Runtime

Stop the Spice runtime and close the SQL REPL when done.

### Step 6: (Optional) Cleanup

Remove the created files:

```shell
# Remove the spicepod.yaml
rm spicepod.yaml

# Remove the Parquet file
rm yellow_tripdata_2024-01.parquet
```

## Query Markdown Documents

Follow these steps to use local Markdown files as a dataset.

### Step 1: Download Markdown Documents

Download sample Markdown files using the following script:

```shell
base_url="https://raw.githubusercontent.com/spiceai/docs/refs/heads/trunk/website/docs/components/data-connectors"

files=(
  "clickhouse.md"
  "databricks.md"
  "debezium.md"
  "delta-lake.md"
)

for file in "${files[@]}"; do
  curl -O "$base_url/$file"
done
```

### Step 2: Create the Spicepod (Markdown dataset)

Create a `spicepod.yaml` file to define your dataset:

```shell
cat <<EOF > spicepod.yaml
version: v1
kind: Spicepod
name: file_recipe_markdown
datasets:
  - name: docs
    from: file:./
    params:
      file_format: md
EOF
```

### Step 3: Start the Spice Runtime

Run the Spice runtime to load the dataset:

```shell
spice run
```

### Step 4: Query the Dataset Using SQL

Open a new terminal and start the SQL REPL:

```shell
spice sql
```

Then execute a query on the `docs` dataset.

```sql
select location from docs;
```

Expected output:

```text
+---------------------------------------------+
| location                                    |
+---------------------------------------------+
| Users/lukim/dev/cookbook/file/debezium.md   |
| Users/lukim/dev/cookbook/file/databricks.md |
| Users/lukim/dev/cookbook/file/README.md     |
| Users/lukim/dev/cookbook/file/clickhouse.md |
| Users/lukim/dev/cookbook/file/delta-lake.md |
+---------------------------------------------+
```

### Step 5: Terminate the Spice Runtime

Stop the Spice runtime and close the SQL REPL when done.

### Step 6: (Optional) Cleanup

Remove the created files:

```shell
# Remove the spicepod.yaml
rm spicepod.yaml

# Remove the downloaded Markdown files
rm *.md
```

## Additional Resources

For more information, see the [File Data Connector documentation](https://spiceai.org/docs/components/data-connectors/file).
