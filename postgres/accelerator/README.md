# PostgreSQL Data Accelerator

Follow these steps to get started with PostgreSQL as a Data Accelerator.

This recipe will use a demo instance of Postgres. Follow the recipe to create Postgres instance and get started with Postgres as a Data Accelerator. With Postgres as a Data Accelerator, data sourced by Data Connectors can be **locally materialized and accelerated** into an attached Postgres instance. Unlike other Data Accelerators which are local to Spice, this enables other applications to query the accelerated data via a native integration with Postgres, which Spice keeps up-to-date automatically.

## Preparation

- Install [PostgresSQL](https://www.postgresql.org/download/). Once downloaded and installed, run the following commands:

```bash
createdb --help
psql --help
```

- Start postgres server (note: this is an insecure postgres, only use for testing).

```bash
docker run --name postgres -e POSTGRES_HOST_AUTH_METHOD=trust  -d -p 5432:5432 postgres
```

- Configure postgres settings

```bash
export PGHOST=localhost
export PGPORT=5432
export PGUSER=postgres
```

- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).
- An account created with the [Spice.ai Cloud Platform](https://spice.ai).

## Steps

**Step 1.** Create a Postgres database for testing.

Create an empty database `spice_demo` in local Postgres.

```bash
createdb spice_demo
```

Verify the creation of `spice_demo` by openning it with psql CLI.

```bash
psql spice_demo
```

**Step 2.** Initialize a Spice app.

```bash
spice init postgres-demo
cd postgres-demo
```

**Step 3.** [Login](https://docs.spiceai.org/cli/reference/login) to use the [Spice.ai Data Connector](https://docs.spiceai.org/data-connectors/spiceai).

```bash
spice login
```

This will create a `.env` file with the Spice.ai API key in the `postgres-demo` directory.

Also, ensure the `PG_PASS` environment variable is set to the password for your Postgres instance. Environment variables can be specified on the command line when running the Spice runtime, or in the same `.env` file created in Step 3.

```bash
echo "PG_PASS=<password>" >> .env
```

**Step 4.** Start the Spice runtime.

```bash
spice run
```

The Spice runtime terminal will show that Spice Runtime is running.

```console
Spice.ai runtime starting...
2024-05-07T01:01:40.566270Z  INFO spiced: Metrics listening on 127.0.0.1:9090
2024-05-07T01:01:40.566873Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2024-05-07T01:01:40.566960Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2024-05-07T01:01:40.568738Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
```

**Step 5.** Configure the dataset to use Postgres as data accelerator. Copy and paste the configuration below to `spicepod.yaml` in the Spice app.

```yaml
version: v1beta1
kind: Spicepod
name: postgres-demo
datasets:
  - from: spice.ai/eth.recent_blocks
    name: eth_recent_blocks
    acceleration:
      enabled: true
      refresh_mode: full
      refresh_check_interval: 10s
      engine: postgres
      params:
        pg_host: localhost
        pg_user: postgres
        pg_port: 5432
        pg_db: spice_demo
        pg_sslmode: disable
        pg_pass: ${env:PG_PASS}
```

Save the changes to `spicepod.yaml`. The Spice runtime terminal will show that the dataset has been loaded:

```console
2024-05-07T23:56:44.094995Z  INFO runtime: Loaded dataset eth_recent_blocks
2024-05-07T23:56:44.095902Z  INFO runtime::accelerated_table: [refresh] Loading data for dataset eth_recent_blocks
```

Follow the [getting started guide](https://docs.spiceai.org/getting-started) to get started with the Spice.ai runtime.

See the [datasets reference](https://docs.spiceai.org/reference/spicepod/datasets) for more dataset configuration options.

**Step 6.** Run queries against the dataset using the Spice SQL REPL.

In a new terminal, start the Spice SQL REPL

```bash
spice sql
```

You can now now query `eth_recent_blocks` in the runtime.

```sql
select number, "timestamp", hash, transaction_count, gas_used from eth_recent_blocks order by number desc limit 10;
```

```shell
+----------+------------+--------------------------------------------------------------------+-------------------+----------+
| number   | timestamp  | hash                                                               | transaction_count | gas_used |
+----------+------------+--------------------------------------------------------------------+-------------------+----------+
| 19823523 | 1715149295 | 0x6a4619e01fae477b9034981c74908a2cf5110c56828227971a46b798c5c11f1b | 238               | 15921279 |
| 19823522 | 1715149283 | 0x3d02a95cfd236d04476bb80e21df4c8a09f58fb360e36af63518b3b253203c57 | 108               | 8855119  |
| 19823521 | 1715149271 | 0x6696fd2d68eb4a527c9e66a4c0c2ab236e2582f898b626a016cde57c4b034bd0 | 243               | 26104830 |
| 19823520 | 1715149259 | 0x51b62fd46a27ec2bc5fa101088123fe2d34d7822fd76f88c419c19ffc98ecd43 | 325               | 29984648 |
| 19823519 | 1715149247 | 0x7be4da28b09084b1e1c5de0b36f1850bf864e8ab5cdd37c507ca814ebd9151c6 | 43                | 1607845  |
| 19823518 | 1715149235 | 0x24fba85aa5895adba1087539c9cd717e2b864f334881b94dd88c09c78c8daca4 | 152               | 13537024 |
| 19823517 | 1715149223 | 0x52453257ae23dd4c910694031d1045a3a3cf71e1004446b4e9b5107c5e569cf2 | 202               | 20325159 |
| 19823516 | 1715149211 | 0x583a7daceb11037d7974cd771e57c8e66cda0fac4c2fd552ad0fc3f49a32c093 | 207               | 18527037 |
| 19823515 | 1715149199 | 0x4c73f16ec65f84f349692e82b34a800a5c12227ec33349f7b54ebebf4d7908e8 | 142               | 14151725 |
| 19823514 | 1715149187 | 0x7486a3c326ddbc4a30d027b222fd10d7cd4f8bcdba7bca68541442f6c0b34b2a | 179               | 15232250 |
+----------+------------+--------------------------------------------------------------------+-------------------+----------+

Time: 0.010686041 seconds. 10 rows.
```

For more information on using `spice sql`, see the [CLI reference](https://docs.spiceai.org/cli/reference/sql).

`eth_recent_blocks` is locally materialized in PostgreSQL, using `psql` to query the same table `eth_recent_blocks` in PostgreSQL.

```sql
psql spice_demo
```

```sql
select number, "timestamp", hash, transaction_count, gas_used from eth_recent_blocks order by number desc limit 10;
```

```shell
  number  | timestamp  |                                hash                                | transaction_count | gas_used
----------+------------+--------------------------------------------------------------------+-------------------+----------
 19823523 | 1715149295 | 0x6a4619e01fae477b9034981c74908a2cf5110c56828227971a46b798c5c11f1b |               238 | 15921279
 19823522 | 1715149283 | 0x3d02a95cfd236d04476bb80e21df4c8a09f58fb360e36af63518b3b253203c57 |               108 |  8855119
 19823521 | 1715149271 | 0x6696fd2d68eb4a527c9e66a4c0c2ab236e2582f898b626a016cde57c4b034bd0 |               243 | 26104830
 19823520 | 1715149259 | 0x51b62fd46a27ec2bc5fa101088123fe2d34d7822fd76f88c419c19ffc98ecd43 |               325 | 29984648
 19823519 | 1715149247 | 0x7be4da28b09084b1e1c5de0b36f1850bf864e8ab5cdd37c507ca814ebd9151c6 |                43 |  1607845
 19823518 | 1715149235 | 0x24fba85aa5895adba1087539c9cd717e2b864f334881b94dd88c09c78c8daca4 |               152 | 13537024
 19823517 | 1715149223 | 0x52453257ae23dd4c910694031d1045a3a3cf71e1004446b4e9b5107c5e569cf2 |               202 | 20325159
 19823516 | 1715149211 | 0x583a7daceb11037d7974cd771e57c8e66cda0fac4c2fd552ad0fc3f49a32c093 |               207 | 18527037
 19823515 | 1715149199 | 0x4c73f16ec65f84f349692e82b34a800a5c12227ec33349f7b54ebebf4d7908e8 |               142 | 14151725
 19823514 | 1715149187 | 0x7486a3c326ddbc4a30d027b222fd10d7cd4f8bcdba7bca68541442f6c0b34b2a |               179 | 15232250
(10 rows)
```
