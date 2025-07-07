# Glue Data Connector

The AWS Glue Data Connector enables Spice to query a tables registered in an AWS Glue Data Catalog. It supports tables referencing S3 data in Iceberg, Hive-style Parquet, and CSV formats.

This guide demonstrates steps to configure Spice for integration with AWS Glue and query a dataset.

## Prerequisites

- An AWS account with an AWS Glue Data Catalog populated with a table. ([AWS Glue documentation](https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html)).
- AWS credentials with sufficient permissions to access the Glue Catalog and the underlying data in S3.
- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).

## Step 1. Create a new Spicepod

```bash
spice init glue-connector-demo
cd glue-connector-demo
```

## Step 2. Set up AWS Credentials

The Spice runtime must be able to access AWS Glue and the underlying data in S3. Set the following environment variables in a `.env` file in your project directory:

```bash
echo "AWS_ACCESS_KEY_ID=<your-access-key>" >> .env
echo "AWS_SECRET_ACCESS_KEY=<your-secret-key>" >> .env
echo "AWS_REGION=<your-aws-region>" >> .env
```

Replace `<your-access-key>`, `<your-secret-key>`, and `<your-aws-region>` with your actual AWS credentials and preferred region (e.g., `us-east-1`).

## Step 3. Add the AWS Glue Data Connector to `spicepod.yaml`

Edit your `spicepod.yaml` file to include the Glue data connector configuration:

```yaml
datasets:
  - from: glue:tpch.lineitem
    name: lineitem
    params:
      glue_region: ${env:AWS_REGION}
      glue_key: ${env:AWS_ACCESS_KEY_ID}
      glue_secret: ${env:AWS_SECRET_ACCESS_KEY}
```
Here, `tpch` is the name of the database and `lineitem` is the name of the table within the database. The database and table names are separated by a `.`.

> **Note:** The connector currently supports querying tables registered in AWS Glue that reference data stored in S3 as Iceberg tables or tables with parquet or CSV data formats.

## Step 4. Start the Spice runtime

```bash
spice run
```

Observe logs indicating that the Glue data connector was registered and tables were discovered.

Example output:

```bash
2025-06-06T16:38:44.476681Z  INFO runtime::init::dataset: Dataset lineitem registered (glue:tpch.lineitem), results cache enabled.
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
| spice           | public       | lineitem          | BASE TABLE |
| spice           | runtime      | task_history      | BASE TABLE |
+-----------------+--------------+-------------------+------------+
```

Query the table:

```sql
SELECT * FROM lineitem LIMIT 10;
```

Example output:

```bash
+------------+-----------+-----------+--------------+------------+-----------------+------------+--------+--------------+--------------+---------------------+---------------------+---------------------+-------------------+------------+------------------------------------------+
| l_orderkey | l_partkey | l_suppkey | l_linenumber | l_quantity | l_extendedprice | l_discount | l_tax  | l_returnflag | l_linestatus | l_shipdate          | l_commitdate        | l_receiptdate       | l_shipinstruct    | l_shipmode | l_comment                                |
+------------+-----------+-----------+--------------+------------+-----------------+------------+--------+--------------+--------------+---------------------+---------------------+---------------------+-------------------+------------+------------------------------------------+
| 5242311    | 170140    | 7692      | 4            | 38.0000    | 45985.3200      | 0.0600     | 0.0400 | A            | F            | 1992-08-22T00:00:00 | 1992-09-13T00:00:00 | 1992-09-09T00:00:00 | NONE              | MAIL       | furiously pending platelets. quickly fin |
| 5242336    | 122672    | 2673      | 1            | 50.0000    | 84733.5000      | 0.0800     | 0.0200 | N            | O            | 1997-06-08T00:00:00 | 1997-07-08T00:00:00 | 1997-06-16T00:00:00 | NONE              | TRUCK      | latelets wake                            |
| 5242336    | 141801    | 4316      | 2            | 42.0000    | 77397.6000      | 0.0100     | 0.0200 | N            | O            | 1997-07-01T00:00:00 | 1997-05-20T00:00:00 | 1997-07-24T00:00:00 | COLLECT COD       | RAIL       | sits wake against the blithely u         |
| 5242336    | 44690     | 4691      | 3            | 6.0000     | 9808.1400       | 0.0200     | 0.0100 | N            | O            | 1997-07-03T00:00:00 | 1997-06-30T00:00:00 | 1997-07-05T00:00:00 | TAKE BACK RETURN  | FOB        | ecial waters; regular                    |
| 5242336    | 88755     | 3772      | 4            | 41.0000    | 71493.7500      | 0.0100     | 0.0300 | N            | O            | 1997-05-01T00:00:00 | 1997-05-26T00:00:00 | 1997-05-31T00:00:00 | COLLECT COD       | MAIL       | equests use. quickly                     |
| 5242337    | 186090    | 8609      | 1            | 7.0000     | 8232.6300       | 0.0600     | 0.0600 | A            | F            | 1995-01-31T00:00:00 | 1995-01-21T00:00:00 | 1995-02-14T00:00:00 | COLLECT COD       | RAIL       | ts impress. unusual, bold package        |
| 5242337    | 6921      | 6922      | 2            | 24.0000    | 43870.0800      | 0.0000     | 0.0200 | A            | F            | 1995-02-11T00:00:00 | 1995-01-17T00:00:00 | 1995-02-12T00:00:00 | NONE              | RAIL       | e pending                                |
| 5242337    | 112451    | 7474      | 3            | 24.0000    | 35122.8000      | 0.0200     | 0.0400 | A            | F            | 1994-12-18T00:00:00 | 1995-02-01T00:00:00 | 1995-01-15T00:00:00 | DELIVER IN PERSON | MAIL       | hely ironi                               |
| 5242338    | 120710    | 5735      | 1            | 11.0000    | 19037.8100      | 0.0700     | 0.0600 | N            | O            | 1995-11-04T00:00:00 | 1995-12-06T00:00:00 | 1995-11-26T00:00:00 | NONE              | MAIL       | ccounts alongside of the blithely sil    |
| 5242338    | 157598    | 5144      | 2            | 39.0000    | 64568.0100      | 0.0200     | 0.0600 | N            | O            | 1996-01-27T00:00:00 | 1995-12-12T00:00:00 | 1996-01-29T00:00:00 | NONE              | TRUCK      | ickly final foxes cajole furiously ironi |
+------------+-----------+-----------+--------------+------------+-----------------+------------+--------+--------------+--------------+---------------------+---------------------+---------------------+-------------------+------------+------------------------------------------+

Time: 24.456572 seconds. 10 rows.
```

---

## References

- [AWS Glue Documentation](https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html)
- [Spice.ai Glue Documentation](https://docs.spiceai.org/components/data-connectors/glue)
