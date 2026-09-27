# Iceberg Hadoop Catalog Connector

Works with `v1.6.0+`

The Iceberg Catalog Connector supports connecting to Hadoop catalogs, locally or on S3-compatible object storage.

This recipe uses the Spice Runtime to connect to a TPCH dataset, configured on a [RustFS](https://github.com/rustfs/rustfs) S3-compatible object store.

> **Note:** Earlier versions of this recipe used MinIO. The open-source MinIO server and client are archived: the `minio/minio` and `minio/mc` images can no longer be pulled, and `dl.min.io` returns `410 Gone` for the client binary, so the recipe now runs on RustFS instead.

## Prerequisites

- Docker is installed, to run the sample RustFS object store service with Hadoop catalog.
- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).

## Step 1: Start the RustFS Server.

Clone the Spice cookbook repository and navigate to the `iceberg-hadoop` directory:

```bash
git clone https://github.com/spiceai/cookbook.git # Skip if already cloned
cd cookbook/catalogs/iceberg-hadoop
```

Use the provided Docker Compose file to start a RustFS server, create the `hadoop` bucket, and load a TPCH dataset into it with Spark:

```bash
docker compose up -d
```

## Step 2: Start the Spice Runtime.

Once Docker has finished starting, enter into the provided spicepod directory and start the Spice Runtime:

```bash
cd hadoop-catalog-recipe
spice run
```

The Runtime should start and register the TPCH catalog. Example output:

```console
2025-08-07T02:51:43.378364Z  INFO spiced: Starting runtime v1.6.0-unstable-build.9286c3f6c-dev
2025-08-07T02:51:43.379862Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2025-08-07T02:51:43.380067Z  INFO runtime::init::caching: Initialized search results cache; max size: 128.00 MiB, item ttl: 1s, engine: Moka
2025-08-07T02:51:44.179771Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-08-07T02:51:44.181135Z  INFO runtime::init::catalog: Registering catalog 'hadoop' for iceberg
2025-08-07T02:51:44.182557Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-08-07T02:51:44.350073Z  INFO runtime::init::catalog: Registered catalog 'hadoop' with 1 schema and 8 tables
2025-08-07T02:51:44.453020Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

## Step 3: Query the Hadoop Catalog.

In a new terminal, run the Spice SQL REPL and execute an SQL command to read TPCH data from the Hadoop catalog:

```bash
spice sql
```

```sql
SELECT * FROM hadoop.tpch.region;
```

Example output:

```console
+-------------+-------------+---------------------------------------------------------------------------------------------------------------------+
| r_regionkey |    r_name   |                                                      r_comment                                                      |
|    int32    |   varchar   |                                                       varchar                                                       |
+-------------+-------------+---------------------------------------------------------------------------------------------------------------------+
| 0           | AFRICA      | ar packages. regular excuses among the ironic requests cajole fluffily blithely final requests. furiously express p |
| 1           | AMERICA     | s are. furiously even pinto bea                                                                                     |
| 2           | ASIA        | c, special dependencies around                                                                                      |
| 3           | EUROPE      | e dolphins are furiously about the carefully                                                                        |
| 4           | MIDDLE EAST |  foxes boost furiously along the carefully dogged tithes. slyly regular orbits according to the special epit        |
+-------------+-------------+---------------------------------------------------------------------------------------------------------------------+

Time: 0.008017584 seconds. 5 rows.
```

## Step 4: Cleanup.

```bash
docker compose down --volumes --rmi local
```
