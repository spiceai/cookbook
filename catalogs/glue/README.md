# AWS Glue Catalog Connector

The AWS Glue Catalog Connector enables Spice to query tables registered in an AWS Glue Data Catalog. It supports tables referencing S3 data in Iceberg, Hive-style Parquet, and CSV formats.

This guide demonstrates steps to configure Spice for integration with AWS Glue and query datasets.

## Prerequisites

- An AWS account with an AWS Glue Data Catalog populated with one or more tables. ([AWS Glue documentation](https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html))
- AWS credentials with sufficient permissions to access the Glue Catalog and the underlying data in S3.
- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).

## Step 1. Set up AWS Credentials

The Spice runtime must be able to access AWS Glue and the underlying data in S3. Set the following environment variables in a `.env` file in your project directory:

```bash
echo "AWS_ACCESS_KEY_ID=<your-access-key>" >> .env
echo "AWS_SECRET_ACCESS_KEY=<your-secret-key>" >> .env
echo "AWS_REGION=<your-aws-region>" >> .env
```

Replace `<your-access-key>`, `<your-secret-key>`, and `<your-aws-region>` with your actual AWS credentials and preferred region (e.g., `us-east-1`).

## Step 2. Create a new directory and initialize a Spicepod

```bash
mkdir glue-catalog-demo
cd glue-catalog-demo
spice init
```

## Step 3. Add the AWS Glue Catalog Connector to `spicepod.yaml`

Edit your `spicepod.yaml` file to include the Glue catalog configuration:

```yaml
catalogs:
  - from: glue
    name: my_glue_catalog
    include:
      - "<database_name>.<table_name>"
    params:
      glue_auth: key
      glue_region: ${env:AWS_REGION}
      glue_key: ${env:AWS_ACCESS_KEY_ID}
      glue_secret: ${env:AWS_SECRET_ACCESS_KEY}
```

Replace `<database_name>` with the name of your AWS Glue database and `<table_name>` with the name of your AWS Glue table. You can use wildcards to specify multiple databases and/or tables (e.g. "mydatabase.mytable_*").

> **Note:** The connector currently supports querying tables registered in AWS Glue that reference supported S3 data in Iceberg and Hive-style parquet tables.

## Step 4. Start the Spice runtime

```bash
spice run
```

You should see logs indicating that the Glue catalog was registered and tables were discovered.

Example log output:
```bash
2025-05-30T17:53:41.123456Z  INFO runtime::init::catalog: Registering catalog 'my_glue_catalog' for glue
2025-05-30T17:53:41.223456Z  INFO runtime::init::catalog: Registered catalog 'my_glue_catalog' with 1 schema and 2 tables
```

## Step 5. Query a dataset

Start the Spice SQL REPL:

```bash
spice sql
```

List the available tables:

```sql
sql> show tables;
+-----------------+--------------+-------------------+------------+
| table_catalog   | table_schema | table_name        | table_type |
+-----------------+--------------+-------------------+------------+
| my_glue_catalog | testdb       | hive_table_001    | BASE TABLE |
| my_glue_catalog | testdb       | iceberg_table_001 | BASE TABLE |
| spice           | runtime      | task_history      | BASE TABLE |
+-----------------+--------------+-------------------+------------+
```

Query a table (replace `testdb.iceberg_table_001` with your actual table name):

```sql
SELECT * FROM my_glue_catalog.testdb.iceberg_table_001 LIMIT 10;
```

Example output:

```bash
+----+--------+-------+---------------------+
| id | name   | value | date                |
+----+--------+-------+---------------------+
| 0  | name_0 | 0.0   | 2023-01-01T00:00:00 |
| 1  | name_1 | 10.5  | 2023-01-02T00:00:00 |
| 2  | name_2 | 21.0  | 2023-01-03T00:00:00 |
| 3  | name_3 | 31.5  | 2023-01-04T00:00:00 |
| 4  | name_4 | 42.0  | 2023-01-05T00:00:00 |
| 5  | name_5 | 52.5  | 2023-01-06T00:00:00 |
| 6  | name_6 | 63.0  | 2023-01-07T00:00:00 |
| 7  | name_7 | 73.5  | 2023-01-08T00:00:00 |
| 8  | name_8 | 84.0  | 2023-01-09T00:00:00 |
| 9  | name_9 | 94.5  | 2023-01-10T00:00:00 |
+----+--------+-------+---------------------+

Time: 5.178558917 seconds. 10 rows.
```

```sql
SELECT * FROM my_glue_catalog.testdb.hive_table_001 LIMIT 10;
```

Example output:

```bash
+----+--------+-------+-------------------+------+-------+
| id | name   | value | __index_level_0__ | year | month |
+----+--------+-------+-------------------+------+-------+
| 0  | name_0 | 0.0   | 0                 | 2023 | 1     |
| 1  | name_1 | 10.5  | 1                 | 2023 | 2     |
| 2  | name_2 | 21.0  | 2                 | 2023 | 3     |
| 3  | name_3 | 31.5  | 3                 | 2023 | 4     |
| 4  | name_4 | 42.0  | 4                 | 2023 | 5     |
| 5  | name_5 | 52.5  | 5                 | 2024 | 1     |
| 6  | name_6 | 63.0  | 6                 | 2024 | 2     |
| 7  | name_7 | 73.5  | 7                 | 2024 | 3     |
| 8  | name_8 | 84.0  | 8                 | 2024 | 4     |
| 9  | name_9 | 94.5  | 9                 | 2024 | 5     |
+----+--------+-------+-------------------+------+-------+

Time: 14.702751 seconds. 10 rows.
```

---

## References

- [AWS Glue Documentation](https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html)
- [Spice.ai Documentation](https://docs.spiceai.org/components/catalogs/glue)
