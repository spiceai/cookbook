# Distributed Query

Works with `v2.0+`

This recipe demonstrates how to run Spice.ai OSS in a distributed mode, for maximum performance in queries on large datasets across multiple nodes. It shows how to:

- Generate mTLS certificates for development environments
- Setup Spice.ai OSS schedulers and executors
- Run distributed Spice.ai queries

## Prerequisites

- [Spice CLI](https://docs.spiceai.org/getting-started) installed

## Getting Started

### Step 1: Prepare Working Directory

Clone the cookbook repository, and change into the recipe directory.

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/distributed
```

### Step 2: Generate Development mTLS Certificates

The Spice CLI provides a helper utility to generate mTLS certificates and a certificate authority for running Spice in clustered mode.

These certificates are not recommended for production use.

Initialize the Spice CA and generate some certificates for the scheduler and executor:

```bash
spice cluster tls init
spice cluster tls add scheduler1
spice cluster tls add executor1
```

### Step 3: Start the Spice Scheduler

Start the Spice scheduler by providing the cluster certificates and cluster mode:

```bash
~/.spice/bin/spiced  --role scheduler \
  --node-bind-address 127.0.0.1:50052 \
  --node-advertise-address 127.0.0.1 \
  --http 127.0.0.1:8090 \
  --flight 127.0.0.1:50051 \
  --node-mtls-ca-certificate-file ~/.spice/pki/ca.crt  \
  --node-mtls-certificate-file ~/.spice/pki/scheduler1.crt \
  --node-mtls-key-file ~/.spice/pki/scheduler1.key
```

The prepared `spicepod.yaml` serves a hive-partitioned dataset from the scheduler to make available for query by all executors:

```yaml
version: v1
kind: Spicepod
name: distributed-query

runtime:
  scheduler:
    state_location: file:///tmp/spice-cluster

datasets:
  - from: s3://spiceai-public-datasets/hive_partitioned_data/
    name: data
    params:
      file_format: parquet
```

The Spice scheduler will now start:

```console
2026-08-02T12:08:34.498489Z  INFO spiced: Starting runtime v2.1.2+models
2026-08-02T12:08:34.500314Z  INFO runtime::cluster::pki: Cluster mTLS configured with CA CN=Spice.ai CLI Root CA - DO NOT USE IN PRODUCTION, OU=unknown and node certificate CN scheduler1
2026-08-02T12:08:34.501762Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2026-08-02T12:08:34.501811Z  INFO runtime::init::caching: Initialized search results cache; max size: 128.00 MiB, item ttl: 1s, engine: Moka
2026-08-02T12:08:34.501832Z  INFO runtime::init::caching: Initialized embeddings cache; max size: 128.00 MiB, item ttl: 1s, engine: Moka
2026-08-02T12:08:34.503488Z  INFO runtime::cluster: Scheduler using shared object-store job state state_location=file:///tmp/spice-cluster
2026-08-02T12:08:34.503505Z  INFO runtime::init::task_history: Task history enabled: retention_period=28800s, retention_check_interval=900s
2026-08-02T12:08:34.503592Z  INFO runtime::init::dataset: Dataset data initializing...
2026-08-02T12:08:34.503770Z  INFO runtime::cluster: Starting Ballista scheduler on 127.0.0.1:50052 (shuffle_format=arrow_ipc, shuffle_location=disk (temp_directory))
2026-08-02T12:08:34.503790Z  INFO ballista_scheduler::scheduler_process: Starting Scheduler grpc server with task scheduling policy of PullStaged
2026-08-02T12:08:34.503818Z  INFO ballista_scheduler::scheduler_server::query_stage_scheduler: Starting QueryStageScheduler
2026-08-02T12:08:34.503839Z  INFO ballista_core::event_loop: Starting the event loop query_stage
2026-08-02T12:08:34.503958Z  INFO runtime::cluster::servers: Cluster mTLS enabled for internal cluster server
2026-08-02T12:08:34.504057Z  INFO runtime::cluster::scheduler_registry: Initialized async SQL jobs API with state location: file:///tmp/spice-cluster
2026-08-02T12:08:34.504088Z  INFO runtime::cluster::servers: Spice Runtime internal cluster server listening on 127.0.0.1:50052
2026-08-02T12:08:34.504479Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2026-08-02T12:08:34.504962Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2026-08-02T12:08:39.554871Z  INFO runtime::init::dataset: Dataset data registered (s3://spiceai-public-datasets/hive_partitioned_data/), results cache enabled. duration_ms=0
2026-08-02T12:08:39.658898Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

### Step 4: Start the Spice Executor

A scheduler requires at least one executor to perform queries. In a new terminal window, change directory back to the distributed query cookbook to access the certificates and start the executor.

A Spice executor does not require a `spicepod.yaml`, as the scheduler will sync dataset information with executors when executing queries:

```bash
~/.spice/bin/spiced --role executor \
  --http 127.0.0.1:9090 \
  --scheduler-address 127.0.0.1:50052 \
  --node-mtls-ca-certificate-file ~/.spice/pki/ca.crt \
  --node-mtls-certificate-file ~/.spice/pki/executor1.crt \
  --node-mtls-key-file ~/.spice/pki/executor1.key \
  --node-bind-address 127.0.0.1:50062 \
  --node-advertise-address 127.0.0.1
```

The Spice executor will now start:

```console
2026-08-02T12:09:07.161124Z  INFO spiced: Starting runtime v2.1.2+models
2026-08-02T12:09:07.161567Z  INFO runtime::cluster::pki: Cluster mTLS configured with CA CN=Spice.ai CLI Root CA - DO NOT USE IN PRODUCTION, OU=unknown and node certificate CN executor1
2026-08-02T12:09:07.162939Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2026-08-02T12:09:07.162988Z  INFO runtime::init::caching: Initialized search results cache; max size: 128.00 MiB, item ttl: 1s, engine: Moka
2026-08-02T12:09:07.163007Z  INFO runtime::init::caching: Initialized embeddings cache; max size: 128.00 MiB, item ttl: 1s, engine: Moka
2026-08-02T12:09:07.164357Z  INFO runtime::init::task_history: Task history enabled: retention_period=28800s, retention_check_interval=900s
2026-08-02T12:09:07.192869Z  INFO runtime::cluster: Scheduler membership: ["127.0.0.1:50052"]
2026-08-02T12:09:07.193318Z  INFO runtime::cluster: Executor shuffle configuration: shuffle_format=arrow_ipc, shuffle_location=disk (temp_directory), work_dir=/var/folders/0g/y7w681p562s3wqh76kkvm_1h0000gn/T/
2026-08-02T12:09:07.193487Z  INFO runtime::cluster::servers: Cluster mTLS enabled for executor flight server
2026-08-02T12:09:07.193495Z  INFO runtime::http: Spice Runtime HTTP health endpoint listening on 127.0.0.1:9090
2026-08-02T12:09:07.267046Z  INFO runtime: All components are loaded. Spice runtime is ready!
2026-08-02T12:09:07.348071Z  INFO ballista_executor::execution_loop: Starting poll work loop with scheduler
2026-08-02T12:09:07.393588Z  INFO runtime::cluster::servers: Spice Runtime executor Flight listening on 127.0.0.1:50062
```

### Step 5: Perform a distributed query

> **Note:** From `v2.0` onwards, queries are distributed across the cluster when they are
> submitted as **async queries** — via `spice query` or `POST /v1/queries`. Ordinary
> Flight SQL queries (`spice sql`, `spice -sql`) are executed locally by the scheduler and
> do not create cluster jobs.

Submit a query with `spice query`. The CLI submits the query to the scheduler and polls until
it completes:

```bash
spice query "select * from data limit 10;"
```

```console
Submitted query: 019FC-263-30F-124214 (RUNNING)
Waiting for completion... (Ctrl+C to stop waiting)
✓ SUCCEEDED (1.5s)
+-------+---------+
|   id  |  value  |
| int64 | varchar |
+-------+---------+
| 0     | value_0 |
| 1     | value_1 |
| 2     | value_2 |
| 3     | value_3 |
| 4     | value_4 |
| 5     | value_5 |
| 6     | value_6 |
| 7     | value_7 |
| 8     | value_8 |
| 9     | value_9 |
+-------+---------+

Time: 1.50428063 seconds. 10 rows.
```

Observing the logs from the scheduler and executor shows the scheduler queuing and planning the
job, and the executor receiving and executing its tasks:

```console
2026-08-02T12:11:48.340741Z  INFO ballista_scheduler::scheduler_server::query_stage_scheduler: Job 019FC-263-30F-124214 queued with name "019FC-263-30F-124214"
2026-08-02T12:11:48.722226Z  INFO ballista_scheduler::planner: planning query stages for job 019FC-263-30F-124214
2026-08-02T12:11:49.251477Z  INFO ballista_scheduler::state::execution_graph: Job 019FC-263-30F-124214 is success, finalizing output partitions
2026-08-02T12:11:49.251561Z  INFO ballista_scheduler::scheduler_server::query_stage_scheduler: Job 019FC-263-30F-124214 success
```

```console
2026-08-02T12:11:48.728085Z  INFO ballista_executor::execution_loop: Received task: [TID 0 019FC-263-30F-124214/1.0/0.0]
2026-08-02T12:11:48.728685Z  INFO ballista_executor::execution_loop: Received task: [TID 1 019FC-263-30F-124214/1.0/1.0]
2026-08-02T12:11:49.047274Z  INFO ballista_executor::execution_loop: Done with task TID 0 019FC-263-30F-124214/1.0/0.0
2026-08-02T12:11:49.074492Z  INFO ballista_executor::execution_loop: Done with task TID 1 019FC-263-30F-124214/1.0/1.0
2026-08-02T12:11:49.146964Z  INFO ballista_executor::execution_loop: Received task: [TID 2 019FC-263-30F-124214/2.0/0.0]
2026-08-02T12:11:49.148574Z  INFO ballista_core::execution_plans::shuffle_writer: Executed partition 0 in 0 seconds. Statistics: numBatches=Some(1), numRows=Some(10), numBytes=Some(65910)
2026-08-02T12:11:49.148640Z  INFO ballista_executor::execution_loop: Done with task TID 2 019FC-263-30F-124214/2.0/0.0
2026-08-02T12:11:49.148703Z  INFO ballista_executor: Task 2 finished with operator_metrics array size 3
```

## Learn More

- [Distributed Query Documentation](https://spiceai.org/docs/features/distributed-query)
- [Async Queries Recipe](../async-queries/README.md) — the async queries API, pagination, and the `spice query` REPL
- [S3 Connector Documentation](https://spiceai.org/docs/components/data-connectors/s3)
