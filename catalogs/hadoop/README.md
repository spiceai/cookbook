# Iceberg Hadoop Catalog Connector

The Iceberg Catalog Connector supports connecting to Hadoop catalogs, locally or on S3-compatible object storage.

This recipe uses the Spice Runtime to connect to a TPCH dataset, configured on a MinIO Object Store.

## Prerequisites

- Docker is installed, to run the sample MinIO object store service with Hadoop catalog.
- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).

## Step 1: Start the MinIO Server

Use the provided Docker Compose file to start a MinIO server, which sets up with a TPCH dataset:

```bash
cd catalogs/hadoop
docker compose up -d
```

## Step 2: Start the Spice Runtime

Once Docker has finished starting, enter into the provided spicepod directory and start the Spice Runtime:

```bash
cd hadoop-catalog-recipe
spice run
```

The Runtime should start and register the TPCH catalog. Example output:

```console
2025-08-07T02:51:43.378364Z  INFO spiced: Starting runtime v1.6.0-unstable-build.9286c3f6c-dev
2025-08-07T02:51:43.379862Z  INFO runtime::init::caching: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2025-08-07T02:51:43.380067Z  INFO runtime::init::caching: Initialized search results cache;
2025-08-07T02:51:44.179771Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-08-07T02:51:44.179840Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2025-08-07T02:51:44.181135Z  INFO runtime::init::catalog: Registering catalog 'hadoop' for iceberg
2025-08-07T02:51:44.182557Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-08-07T02:51:44.350073Z  INFO runtime::init::catalog: Registered catalog 'hadoop' with 1 schema and 8 tables
2025-08-07T02:51:44.453020Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

## Step 3: Query the Hadoop Catalog

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
| r_regionkey | r_name      | r_comment                                                                                                           |
+-------------+-------------+---------------------------------------------------------------------------------------------------------------------+
| 0           | AFRICA      | ar packages. regular excuses among the ironic requests cajole fluffily blithely final requests. furiously express p |
| 1           | AMERICA     | s are. furiously even pinto bea                                                                                     |
| 2           | ASIA        | c, special dependencies around                                                                                      |
| 3           | EUROPE      | e dolphins are furiously about the carefully                                                                        |
| 4           | MIDDLE EAST |  foxes boost furiously along the carefully dogged tithes. slyly regular orbits according to the special epit        |
+-------------+-------------+---------------------------------------------------------------------------------------------------------------------+
```
