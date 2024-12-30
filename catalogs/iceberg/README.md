# Iceberg Catalog Connector

The Iceberg Catalog Connector enables Spice to query Iceberg tables in an Iceberg catalog.

## Prerequisites

- Access to an Iceberg catalog, or Docker to run an Iceberg catalog locally.
- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).

## Step 1. Create a new directory and initialize a Spicepod

```bash
mkdir iceberg-catalog-recipe
cd iceberg-catalog-recipe
spice init
```

## Step 2. Run the Docker container for the Iceberg catalog

In a separate terminal, clone the cookbook repository and run the Docker container for the Iceberg catalog.

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/catalogs/iceberg
docker compose up -d
```

## Step 3. Add the Iceberg Catalog Connector to your Spicepod

`spicepod.yaml`

```yaml
catalogs:
  - from: iceberg:http://localhost:8181/v1/namespaces
    name: ice
    params:
      iceberg_s3_endpoint: http://localhost:9000
      iceberg_s3_access_key_id: admin
      iceberg_s3_secret_access_key: password
      iceberg_s3_region: us-east-1
```

## Step 4. Run Spice

```bash
spice run
```

## Step 5. Query the Iceberg catalog

```bash
spice sql
sql> SELECT * FROM ice.nyc.taxis LIMIT 10;
```

Output:

```bash
Welcome to the Spice.ai SQL REPL! Type 'help' for help.

show tables; -- list available tables
sql> SELECT * FROM ice.nyc.taxis LIMIT 10;
+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+
| VendorID | tpep_pickup_datetime | tpep_dropoff_datetime | passenger_count | trip_distance | RatecodeID | store_and_fwd_flag | PULocationID | DOLocationID | payment_type | fare_amount | extra | mta_tax | tip_amount | tolls_amount | improvement_surcharge | total_amount | congestion_surcharge | airport_fee |
+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+
| 1        | 2021-04-01T00:00:18  | 2021-04-01T00:21:54   | 1.0             | 8.4           | 1.0        | N                  | 79           | 116          | 1            | 25.5        | 3.0   | 0.5     | 5.85       | 0.0          | 0.3                   | 35.15        | 2.5                  | 0.0         |
| 1        | 2021-04-01T00:42:37  | 2021-04-01T00:46:23   | 1.0             | 0.9           | 1.0        | N                  | 75           | 236          | 2            | 5.0         | 3.0   | 0.5     | 0.0        | 0.0          | 0.3                   | 8.8          | 2.5                  | 0.0         |
| 1        | 2021-04-01T00:57:56  | 2021-04-01T01:08:22   | 1.0             | 3.4           | 1.0        | N                  | 236          | 168          | 2            | 11.5        | 3.0   | 0.5     | 0.0        | 0.0          | 0.3                   | 15.3         | 2.5                  | 0.0         |
| 1        | 2021-04-01T00:01:58  | 2021-04-01T00:54:27   | 1.0             | 0.0           | 1.0        | N                  | 47           | 61           | 1            | 44.2        | 0.0   | 0.5     | 0.0        | 0.0          | 0.3                   | 45.0         | 0.0                  | 0.0         |
| 2        | 2021-04-01T00:24:55  | 2021-04-01T00:34:33   | 1.0             | 1.96          | 1.0        | N                  | 238          | 152          | 1            | 9.0         | 0.5   | 0.5     | 3.09       | 0.0          | 0.3                   | 13.39        | 0.0                  | 0.0         |
| 2        | 2021-04-01T00:19:16  | 2021-04-01T00:21:46   | 1.0             | 0.77          | 1.0        | N                  | 142          | 238          | 1            | 4.5         | 0.5   | 0.5     | 1.24       | 0.0          | 0.3                   | 9.54         | 2.5                  | 0.0         |
| 2        | 2021-04-01T00:25:11  | 2021-04-01T00:31:53   | 1.0             | 3.65          | 1.0        | N                  | 238          | 244          | 1            | 11.5        | 0.5   | 0.5     | 2.56       | 0.0          | 0.3                   | 15.36        | 0.0                  | 0.0         |
| 1        | 2021-04-01T00:27:53  | 2021-04-01T00:47:03   | 0.0             | 8.9           | 1.0        | N                  | 138          | 239          | 1            | 26.5        | 3.0   | 0.5     | 7.25       | 6.12         | 0.3                   | 43.67        | 2.5                  | 0.0         |
| 2        | 2021-04-01T00:24:24  | 2021-04-01T00:37:50   | 1.0             | 2.98          | 1.0        | N                  | 151          | 244          | 2            | 12.0        | 0.5   | 0.5     | 0.0        | 0.0          | 0.3                   | 13.3         | 0.0                  | 0.0         |
| 1        | 2021-04-01T00:19:18  | 2021-04-01T00:41:25   | 1.0             | 8.9           | 1.0        | N                  | 132          | 196          | 2            | 28.0        | 0.5   | 0.5     | 0.0        | 0.0          | 0.3                   | 29.3         | 0.0                  | 0.0         |
+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+

Time: 0.186233833 seconds. 10 rows.
```

