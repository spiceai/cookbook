# Distributed Query

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
spiced --role scheduler --scheduler-address 0.0.0.0:50052 --node-mtls-ca-certificate-file ~/.spice/pki/ca.crt --node-mtls-certificate-file ~/.spice/pki/scheduler1.crt --node-mtls-key-file ~/.spice/pki/scheduler1.key --node-advertise-address localhost:50052
```

The prepared `spicepod.yaml` serves a hive-partitioned dataset from the scheduler to make available for query by all executors:

```yaml
version: v1
kind: Spicepod
name: distributed-query

datasets:
  - from: s3://spiceai-public-datasets/hive_partitioned_data/
    name: data
    params:
      file_format: parquet
```

The Spice scheduler will now start:

```console
2025-12-15T23:14:49.338208Z  INFO spiced: Starting runtime v1.10.1-unstable-build.0877656da-dev
2025-12-15T23:14:49.344851Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2025-12-15T23:14:49.345065Z  INFO runtime::init::caching: Initialized search results cache; max size: 128.00 MiB, item ttl: 1s
2025-12-15T23:14:49.345164Z  INFO runtime::init::caching: Initialized embeddings cache; max size: 128.00 MiB, item ttl: 1s
2025-12-15T23:14:50.185537Z  INFO runtime::cluster: Starting Ballista scheduler on 0.0.0.0:50052
2025-12-15T23:14:50.185608Z  INFO ballista_scheduler::scheduler_process: Starting Scheduler grpc server with task scheduling policy of PullStaged
2025-12-15T23:14:50.185612Z  INFO runtime::init::task_history: Task history enabled: retention_period=28800s, retention_check_interval=900s
2025-12-15T23:14:50.185719Z  INFO ballista_scheduler::scheduler_server::query_stage_scheduler: Starting QueryStageScheduler
2025-12-15T23:14:50.185866Z  WARN runtime: Distributed Query (Alpha) is in preview and should not be used in production.
2025-12-15T23:14:50.186108Z  INFO runtime::init::dataset: Dataset data initializing...
2025-12-15T23:14:50.186157Z  INFO ballista_core::event_loop: Starting the event loop query_stage
2025-12-15T23:14:50.186890Z  INFO runtime::cluster::servers: Cluster mTLS enabled for internal cluster server
2025-12-15T23:14:50.186996Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-12-15T23:14:50.187124Z  INFO runtime::cluster::servers: Spice Runtime internal cluster server listening on 0.0.0.0:50052
2025-12-15T23:14:50.194372Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-12-15T23:14:52.097222Z  INFO runtime::init::dataset: Dataset data registered (s3://spiceai-public-datasets/hive_partitioned_data/), results cache enabled.
2025-12-15T23:14:52.199645Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

### Step 4: Start the Spice Executor

A scheduler requires at least one executor to perform queries. In a new terminal window, change directory back to the distributed query cookbook to access the certificates and start the executor.

A Spice executor does not require a `spicepod.yaml`, as the scheduler will sync dataset information with executors when executing queries:

```bash
spiced --role executor --scheduler-address 0.0.0.0:50053 --node-mtls-ca-certificate-file ~/.spice/pki/ca.crt --node-mtls-certificate-file ~/.spice/pki/executor1.crt --node-mtls-key-file ~/.spice/pki/executor1.key --node-mtls-scheduler-url https://localhost:50052 --node-advertise-address localhost:50053
```

The Spice executor will now start:

```console
2025-12-15T23:16:55.196064Z  INFO spiced: Starting runtime v1.10.1-unstable-build.0877656da-dev
2025-12-15T23:16:55.201816Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2025-12-15T23:16:55.202032Z  INFO runtime::init::caching: Initialized search results cache; max size: 128.00 MiB, item ttl: 1s
2025-12-15T23:16:55.202128Z  INFO runtime::init::caching: Initialized embeddings cache; max size: 128.00 MiB, item ttl: 1s
2025-12-15T23:16:56.023942Z  INFO runtime::init::task_history: Task history enabled: retention_period=28800s, retention_check_interval=900s
2025-12-15T23:16:56.053505Z  WARN runtime: Distributed Query (Alpha) is in preview and should not be used in production.
2025-12-15T23:16:56.053559Z  INFO ballista_executor::execution_loop: Starting poll work loop with scheduler
2025-12-15T23:16:56.053746Z  INFO runtime::cluster::servers: Cluster mTLS enabled for executor flight server
2025-12-15T23:16:56.053952Z  INFO runtime::cluster::servers: Spice Runtime executor Flight listening on [::1]:50053
2025-12-15T23:16:56.092402Z  INFO runtime::cluster: Configured object storage for Dataset data
2025-12-15T23:16:56.128100Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

### Step 5: Perform a query

Start the Spice SQL REPL and perform a query against the distributed dataset:

```bash
spice sql
```

```sql
select * from data limit 10;
```

Observing the logs from the scheduler and executor shows the scheduler queuing the job, and the executor receiving and executing it:

```console
2025-12-15T23:18:12.527307Z  INFO ballista_scheduler::scheduler_server::grpc: execution query - session_id: c4e24be7-23e1-427f-963b-fa43e0e3e5c7, operation_id: 019b244e-a513-70c0-b1eb-d3cace68f45e, job_name: , job_id: obUkdkM
2025-12-15T23:18:12.528591Z  INFO ballista_scheduler::scheduler_server::query_stage_scheduler: Job dyHURMz queued with name ""
2025-12-15T23:18:12.530719Z  INFO ballista_core::execution_plans::distributed_query: Job dyHURMz is queued...
2025-12-15T23:18:14.179762Z  INFO ballista_scheduler::planner: planning query stages for job dyHURMz
```

```console
2025-12-15T23:18:15.936693Z  INFO ballista_executor::execution_loop: Received task: [TID 2 dyHURMz/2.0/0.0]
2025-12-15T23:18:15.943448Z  INFO ballista_core::execution_plans::shuffle_writer: Executed partition 0 in 0 seconds. Statistics: numBatches=Some(1), numRows=Some(10), numBytes=Some(454)
2025-12-15T23:18:15.943509Z  INFO ballista_executor::metrics: === [dyHURMz/2/0] Physical plan with metrics ===
DefaultQueryStageExec: (write_time{partition=0}=3.050939ms, repart_time{partition=0}=NOT RECORDED, input_rows{partition=0}=10, output_rows{partition=0}=10)
ShuffleWriterExec: job=dyHURMz stage=2 work_dir=/tmp partitioning=None plan: 
 CoalescePartitionsExec: fetch=10, statistics=[Rows=Exact(10), Bytes=Absent, [(Col[0]:),(Col[1]:)]]
  ShuffleReaderExec: partitioning=UnknownPartitioning(2), statistics=[Rows=Exact(20), Bytes=Exact(1104), [(Col[0]:),(Col[1]:)]]


2025-12-15T23:18:15.943625Z  INFO ballista_executor::execution_loop: Done with task TID 2 dyHURMz/2.0/0.0
2025-12-15T23:18:15.943663Z  INFO ballista_executor: Task 2 finished with operator_metrics array size 3
```

The query will complete and return results to the Spice SQL REPL:

```console
+----+---------+
| id | value   |
+----+---------+
| 30 | value_0 |
| 31 | value_1 |
| 32 | value_2 |
| 33 | value_3 |
| 34 | value_4 |
| 35 | value_5 |
| 36 | value_6 |
| 37 | value_7 |
| 38 | value_8 |
| 39 | value_9 |
+----+---------+

Time: 3.623779129 seconds. 10 rows.
```

## Learn More

- [Distributed Query Documentation](https://spiceai.org/docs/features/distributed-query)
- [S3 Connector Documentation](https://spiceai.org/docs/components/data-connectors/s3)