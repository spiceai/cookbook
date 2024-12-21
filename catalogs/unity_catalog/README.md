# Unity Catalog Connector

The Unity Catalog Connector makes querying tables in a Unity Catalog with Spice simple.

Note: This recipe applies to the [open-source version of Unity Catalog](https://www.unitycatalog.io/). To get started with the Databricks Unity Catalog Connector, see the [Databricks Unity Catalog Connector recipe](../databricks/README.md).

## Prerequisites

- Access to an open-source Unity Catalog server with 1+ tables. (see the [Unity Catalog documentation](https://github.com/unitycatalog/unitycatalog)).
- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).

## Step 1. Create a new directory and initialize a Spicepod

```bash
mkdir uc-catalog-demo
cd uc-catalog-demo
spice init
```

## Step 2. Add the Unity Catalog Connector to `spicepod.yaml`

Add the following configuration to your `spicepod.yaml`:

```yaml
catalogs:
  - from: unity_catalog:https://<unity_catalog_host>/api/2.1/unity-catalog/catalogs/<catalog_name>
    name: uc
    params:
      # Configure the object store credentials here. Not required when running Unity Catalog locally.
```

The Unity Catalog connector only supports Delta Lake tables and requires specifying the object store credentials to connect to the Delta Lake tables.

Visit the documentation for more information configuring the [Unity Catalog Connector](https://docs.spiceai.org/components/catalogs/unity-catalog).

## Step 3. Configure the object store credentials

Configure credentials for the underlying Delta Lake tables object store.

### AWS S3

```yaml
params:
  unity_catalog_aws_access_key_id: ${env:AWS_ACCESS_KEY_ID}
  unity_catalog_aws_secret_access_key: ${env:AWS_SECRET_ACCESS_KEY}
  unity_catalog_aws_region: <region> # E.g. us-east-1, us-west-2
  unity_catalog_aws_endpoint: <endpoint> # If using an S3-compatible service, like Minio
```

Set the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables to the AWS access key and secret key, respectively.

### Azure Blob Storage

```yaml
params:
  mode: delta_lake
  unity_catalog_azure_storage_account_name: ${env:AZURE_ACCOUNT_NAME}
  unity_catalog_azure_account_key: ${env:AZURE_ACCOUNT_KEY}
```

Set the `AZURE_ACCOUNT_NAME` and `AZURE_ACCOUNT_KEY` environment variables to the Azure storage account name and account key, respectively.

### Google Cloud Storage

```yaml
params:
  mode: delta_lake
  unity_catalog_google_service_account: </path/to/service-account.json>
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
SELECT * FROM uc.<SCHEMA_NAME>.<TABLE_NAME> LIMIT 10;
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
