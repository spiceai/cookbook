# Databricks Unity Catalog Connector

The Databricks Unity Catalog Connector makes querying Databricks Unity Catalog tables in Spice simple.

## Prerequisites

- A Databricks account with a Unity Catalog configured with 1 or more tables. (see the [Databricks documentation](https://docs.databricks.com/en/data-governance/unity-catalog/index.html) for more information).
- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).

## Step 1. Create a Databricks API token

Create a Databricks personal access token by following the [Databricks documentation](https://docs.databricks.com/en/dev-tools/auth/index.html).

## Step 2. Create a new directory and initialize a Spicepod

```bash
mkdir databricks-catalog-demo
cd databricks-catalog-demo
spice init
```

## Step 3. Add the Databricks Unity Catalog Connector to `spicepod.yaml`

Add the following configuration to your `spicepod.yaml`:

```yaml
catalogs:
  - from: databricks:<CATALOG_NAME>
    name: db_uc
    params:
      mode: spark_connect # or delta_lake
      databricks_token: ${env:DATABRICKS_TOKEN}
      databricks_endpoint: <instance-id>.cloud.databricks.com
      databricks_cluster_id: <cluster-id>
```

For `mode` you can choose between `spark_connect` or `delta_lake`. `spark_connect` is the default mode and requires an [All-Purpose Compute Cluster](https://docs.databricks.com/en/compute/index.html) to be available. `delta_lake` mode queries directly against Delta Lake tables in object storage, and requires Spice to have the necessary permissions to access the object storage directly.

Set the `DATABRICKS_TOKEN` environment variable to the Databricks personal access token created in Step 1. A `.env` file created in the same directory as `spicepod.yaml` can be used to set the variable, i.e.:

```bash
echo "DATABRICKS_TOKEN=<token>" > .env
```

Visit the documentation for more information configuring the [Databricks Unity Catalog Connector](https://docs.spiceai.org/components/catalogs/databricks).

## Step 4. Set the object storage credentials for `delta_lake` mode

When using the `delta_lake` mode, the object storage credentials must be set for Spice to access the data.

### Using Delta Lake directly against AWS S3

```yaml
params:
  mode: delta_lake
  databricks_endpoint: <instance-id>.cloud.databricks.com
  databricks_token: ${env:DATABRICKS_TOKEN}
  databricks_aws_access_key_id: ${env:AWS_ACCESS_KEY_ID}
  databricks_aws_secret_access_key: ${env:AWS_SECRET_ACCESS_KEY}
  databricks_aws_region: <region> # E.g. us-east-1, us-west-2
  databricks_aws_endpoint: <endpoint> # If using an S3-compatible service, like Minio
```

Set the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables to the AWS access key and secret key, respectively.

### Using Delta Lake directly against Azure Blob Storage

```yaml
params:
  mode: delta_lake
  databricks_token: ${env:DATABRICKS_TOKEN}
  databricks_azure_storage_account_name: ${env:AZURE_ACCOUNT_NAME}
  databricks_azure_account_key: ${env:AZURE_ACCOUNT_KEY}
```

Set the `AZURE_ACCOUNT_NAME` and `AZURE_ACCOUNT_KEY` environment variables to the Azure storage account name and account key, respectively.

### Using Delta Lake directly against Google Cloud Storage

```yaml
params:
  mode: delta_lake
  databricks_token: ${env:DATABRICKS_TOKEN}
  databricks_google_service_account: </path/to/service-account.json>
```

## Step 5. Start the Spice runtime

```bash
spice run
```

## Step 6. Query a dataset

```bash
spice sql
```

```sql
SELECT * FROM db_uc.<SCHEMA_NAME>.<TABLE_NAME> LIMIT 10;
```

Example:

```bash
sql> select trace_id, block_number from db_uc.default.traces limit 10;
+-------------------------------------------------------------------------------+--------------+
| trace_id                                                                      | block_number |
+-------------------------------------------------------------------------------+--------------+
| call_0x0e981c555b68e4f7847155e348e75de70729d06a5f3f238dd4e7d4e062a62eed_      | 16876417     |
| call_0xf2e97e476aaba415ad6793e5d09e82d7ef52d7d595db956306c44dc4e08d1f72_      | 16876417     |
| call_0x79be0ec50306a78a79eed5c368a38d17ff7d3d51d0c8331e36914b95d8635ef3_5     | 16876417     |
| call_0x79be0ec50306a78a79eed5c368a38d17ff7d3d51d0c8331e36914b95d8635ef3_5_0   | 16876417     |
| call_0x7997d1a4ea8a7ece16d3a306c1e820de66744b7f340e7a51b78a35fad5d789d0_      | 16876417     |
| call_0x7997d1a4ea8a7ece16d3a306c1e820de66744b7f340e7a51b78a35fad5d789d0_0     | 16876417     |
| call_0x7997d1a4ea8a7ece16d3a306c1e820de66744b7f340e7a51b78a35fad5d789d0_0_0   | 16876417     |
| call_0x7997d1a4ea8a7ece16d3a306c1e820de66744b7f340e7a51b78a35fad5d789d0_0_0_0 | 16876417     |
| call_0x7997d1a4ea8a7ece16d3a306c1e820de66744b7f340e7a51b78a35fad5d789d0_0_1   | 16876417     |
| call_0x7997d1a4ea8a7ece16d3a306c1e820de66744b7f340e7a51b78a35fad5d789d0_0_2   | 16876417     |
+-------------------------------------------------------------------------------+--------------+

Time: 1.5179735 seconds. 10 rows.
```
