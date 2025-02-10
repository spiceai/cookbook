# Running Spice.ai in Kubernetes

**Step 1.** (Optional) Start a local [`kind`](https://kind.sigs.k8s.io/) cluster:

```bash
go install sigs.k8s.io/kind@v0.22.0
kind create cluster
```

See [kind installation](https://kind.sigs.k8s.io/docs/user/quick-start/#installation) for other installation options.

**Step 2.** Install Spice in your Kubernetes cluster using Helm:

```bash
helm repo add spiceai https://helm.spiceai.org
helm install spiceai-dev spiceai/spiceai
```

Output:

```bash
NAME: spiceai-dev
LAST DEPLOYED: Thu Feb  6 16:18:14 2025
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None
```

**Step 3.** Verify that the Spice pods are running:

```bash
kubectl get pods
```

Output:

```bash
NAME                       READY   STATUS    RESTARTS   AGE
spiceai-dev-5dbb7b77bb-9p8p6   1/1     Running   0          22s
```

```bash
kubectl logs spiceai-dev-5dbb7b77bb-9p8p6
# or just
kubectl logs deploy/spiceai-dev
```

Output:

```bash
2024-11-27T21:55:48.116059Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 0.0.0.0:9090
2024-11-27T21:55:48.116119Z  INFO runtime::flight: Spice Runtime Flight listening on 0.0.0.0:50051
2024-11-27T21:55:48.116053Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 0.0.0.0:50052
2024-11-27T21:55:48.116548Z  INFO runtime::http: Spice Runtime HTTP listening on 0.0.0.0:8090
2024-11-27T21:55:48.116578Z  INFO runtime: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
```

**Step 4.** Run the Spice SQL REPL inside the running pod:

```bash
kubectl exec -it deploy/spiceai-dev -- spiced --repl
```

**Step 5.** Run these queries in the Spice SQL REPL:

```sql
show tables;
```

```sql
+---------------+--------------+---------------+------------+
| table_catalog | table_schema | table_name    | table_type |
+---------------+--------------+---------------+------------+
| spice         | runtime      | metrics       | BASE TABLE |
| spice         | runtime      | task_history  | BASE TABLE |
+---------------+--------------+---------------+------------+
```

**Step 6.** Create a `values.yaml` file to configure the Spice deployment. See [Spice Helm Values](https://spiceai.org/docs/deployment/kubernetes#values) for more deails.

```bash
cat <<EOF > values.yaml
spicepod:
  name: app
  version: v1
  kind: Spicepod

  datasets:
    - from: s3://spiceai-demo-datasets/taxi_trips/2024/
      name: taxi_trips_customized
      description: Demo taxi trips in s3
      params:
        file_format: parquet
      acceleration:
        enabled: true
EOF
```

**Step 7.** Update the Spice deployment with the new configuration:

```bash
helm upgrade spiceai-dev spiceai/spiceai -f values.yaml
```

Output:

```bash
Release "spiceai-dev" has been upgraded. Happy Helming!
NAME: spiceai-dev
LAST DEPLOYED: Thu Feb  6 16:23:20 2025
NAMESPACE: default
STATUS: deployed
REVISION: 2
TEST SUITE: None
```

**Step 8.** Rerun the Spice SQL REPL

```bash
kubectl exec -it deploy/spiceai-dev -- spiced --repl
```

**Step 9.** Run these queries in the Spice SQL REPL:

```sql
show tables;
```

```sql
+---------------+--------------+-----------------------+------------+
| table_catalog | table_schema | table_name            | table_type |
+---------------+--------------+-----------------------+------------+
| spice         | public       | taxi_trips_customized | BASE TABLE |
| spice         | runtime      | task_history          | BASE TABLE |
| spice         | runtime      | metrics               | BASE TABLE |
+---------------+--------------+-----------------------+------------+
```

```sql
describe taxi_trips_customized;
```

```sql
+-----------------------+------------------------------+-------------+
| column_name           | data_type                    | is_nullable |
+-----------------------+------------------------------+-------------+
| VendorID              | Int32                        | YES         |
| tpep_pickup_datetime  | Timestamp(Microsecond, None) | YES         |
| tpep_dropoff_datetime | Timestamp(Microsecond, None) | YES         |
| passenger_count       | Int64                        | YES         |
| trip_distance         | Float64                      | YES         |
| RatecodeID            | Int64                        | YES         |
| store_and_fwd_flag    | Utf8                         | YES         |
| PULocationID          | Int32                        | YES         |
| DOLocationID          | Int32                        | YES         |
| payment_type          | Int64                        | YES         |
| fare_amount           | Float64                      | YES         |
| extra                 | Float64                      | YES         |
| mta_tax               | Float64                      | YES         |
| tip_amount            | Float64                      | YES         |
| tolls_amount          | Float64                      | YES         |
| improvement_surcharge | Float64                      | YES         |
| total_amount          | Float64                      | YES         |
| congestion_surcharge  | Float64                      | YES         |
| Airport_fee           | Float64                      | YES         |
+-----------------------+------------------------------+-------------+

Time: 0.006071083 seconds. 19 rows.
```

```sql
select * from taxi_trips_customized limit 10;
```

```sql
+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+
| VendorID | tpep_pickup_datetime | tpep_dropoff_datetime | passenger_count | trip_distance | RatecodeID | store_and_fwd_flag | PULocationID | DOLocationID | payment_type | fare_amount | extra | mta_tax | tip_amount | tolls_amount | improvement_surcharge | total_amount | congestion_surcharge | Airport_fee |
+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+
| 1        | 2024-01-24T20:40:32  | 2024-01-24T20:53:05   |                 | 2.3           |            |                    | 236          | 230          | 0            | 14.9        | 1.0   | 0.5     | 3.98       | 0.0          | 1.0                   | 23.88        |                      |             |
| 2        | 2024-01-24T20:35:35  | 2024-01-24T20:55:24   |                 | 2.37          |            |                    | 162          | 68           | 0            | 16.88       | 0.0   | 0.5     | 0.0        | 0.0          | 1.0                   | 20.88        |                      |             |
| 1        | 2024-01-24T20:28:26  | 2024-01-24T20:40:36   |                 | 0.0           |            |                    | 229          | 186          | 0            | 13.8        | 0.0   | 0.5     | 0.0        | 0.0          | 1.0                   | 17.8         |                      |             |
| 1        | 2024-01-24T20:10:04  | 2024-01-24T20:21:48   |                 | 0.0           |            |                    | 161          | 141          | 0            | 10.04       | 0.0   | 0.5     | 0.0        | 0.0          | 1.0                   | 14.04        |                      |             |
| 2        | 2024-01-24T20:11:41  | 2024-01-24T20:20:52   |                 | 1.25          |            |                    | 162          | 186          | 0            | 13.69       | 0.0   | 0.5     | 0.0        | 0.0          | 1.0                   | 17.69        |                      |             |
| 2        | 2024-01-24T20:03:00  | 2024-01-24T20:32:00   |                 | 9.95          |            |                    | 263          | 97           | 0            | 44.8        | 0.0   | 0.5     | 4.88       | 0.0          | 1.0                   | 53.68        |                      |             |
| 1        | 2024-01-24T20:22:08  | 2024-01-24T20:25:22   |                 | 0.4           |            |                    | 239          | 142          | 0            | 5.1         | 1.0   | 0.5     | 1.01       | 0.0          | 1.0                   | 11.11        |                      |             |
| 2        | 2024-01-24T20:36:08  | 2024-01-24T20:49:33   |                 | 2.51          |            |                    | 161          | 262          | 0            | 13.9        | 0.0   | 0.5     | 0.0        | 0.0          | 1.0                   | 17.9         |                      |             |
| 2        | 2024-01-24T20:06:35  | 2024-01-24T20:21:08   |                 | 3.94          |            |                    | 236          | 137          | 0            | 19.08       | 0.0   | 0.5     | 0.0        | 0.0          | 1.0                   | 23.08        |                      |             |
| 2        | 2024-01-24T20:24:33  | 2024-01-24T20:42:50   |                 | 2.88          |            |                    | 231          | 107          | 0            | 16.92       | 0.0   | 0.5     | 0.0        | 0.0          | 1.0                   | 20.92        |                      |             |
+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+

Time: 0.01968175 seconds. 10 rows.
```

## Enable Verbose Logging (optional)

Update a `values.yaml`. See [Configuring Trace Levels](https://spiceai.org/docs/cli/tracing) for more details.

```bash
cat <<EOF > values.yaml
additionalEnv:
  - name: SPICED_LOG
    value: "spiced=DEBUG,runtime=DEBUG,secrets=DEBUG,data_components=DEBUG,cache=DEBUG,INFO"

spicepod:
  name: app
  version: v1
  kind: Spicepod

  datasets:
    - from: s3://spiceai-demo-datasets/taxi_trips/2024/
      name: taxi_trips_customized
      description: Demo taxi trips in s3
      params:
        file_format: parquet
      acceleration:
        enabled: true
EOF
```

```bash
helm upgrade spiceai-dev spiceai/spiceai -f values.yaml
```

Output:

```bash
Release "spiceai-dev" has been upgraded. Happy Helming!
NAME: spiceai-dev
LAST DEPLOYED: Thu Feb  6 16:41:00 2025
NAMESPACE: default
STATUS: deployed
REVISION: 3
TEST SUITE: None
```

```bash
kubectl logs deploy/spiceai-dev
```

Observe new debug level traces:

```bash
2025-02-07T00:48:23.429332Z DEBUG runtime::datafusion: Creating accelerated table Dataset { from: "s3://spiceai-demo-datasets/taxi_trips/2024/", name: Bare { table: "taxi_trips_customized" }, mode: Read, params: {"file_format": "parquet"}, metadata: {}, columns: [], has_metadata_table: false, replication: None, time_column: None, time_format: None, acceleration: Some(Acceleration { enabled: true, mode: Memory, engine: Arrow, refresh_mode: None, refresh_check_interval: None, refresh_sql: None, refresh_data_window: None, refresh_append_overlap: None, refresh_retry_enabled: true, refresh_retry_max_attempts: None, refresh_jitter_enabled: false, refresh_jitter_max: None, params: {}, retention_period: None, retention_check_interval: None, retention_check_enabled: false, on_zero_results: ReturnEmpty, indexes: {}, primary_key: None, on_conflict: {}, disable_query_push_down: false }), embeddings: [], app: Some(App { name: "app", secrets: [], extensions: {}, catalogs: [], datasets: [Dataset { from: "s3://spiceai-demo-datasets/taxi_trips/2024/", name: "taxi_trips_customized", description: Some("Demo taxi trips in s3"), metadata: {}, columns: [], mode: Read, params: Some(Params { data: {"file_format": String("parquet")} }), has_metadata_table: None, replication: None, time_column: None, time_format: None, acceleration: Some(Acceleration { enabled: true, mode: Memory, engine: None, refresh_mode: None, refresh_check_interval: None, refresh_sql: None, refresh_data_window: None, refresh_append_overlap: None, refresh_retry_enabled: true, refresh_retry_max_attempts: None, refresh_jitter_enabled: false, refresh_jitter_max: None, params: None, retention_period: None, retention_check_interval: None, retention_check_enabled: false, on_zero_results: ReturnEmpty, ready_state: None, indexes: {}, primary_key: None, on_conflict: {} }), embeddings: [], depends_on: [], invalid_type_action: None, ready_state: OnLoad }], views: [], models: [], embeddings: [], evals: [], tools: [], spicepods: [Spicepod { version: V1, name: "app", extensions: {}, secrets: [], catalogs: [], datasets: [Dataset { from: "s3://spiceai-demo-datasets/taxi_trips/2024/", name: "taxi_trips_customized", description: Some("Demo taxi trips in s3"), metadata: {}, columns: [], mode: Read, params: Some(Params { data: {"file_format": String("parquet")} }), has_metadata_table: None, replication: None, time_column: None, time_format: None, acceleration: Some(Acceleration { enabled: true, mode: Memory, engine: None, refresh_mode: None, refresh_check_interval: None, refresh_sql: None, refresh_data_window: None, refresh_append_overlap: None, refresh_retry_enabled: true, refresh_retry_max_attempts: None, refresh_jitter_enabled: false, refresh_jitter_max: None, params: None, retention_period: None, retention_check_interval: None, retention_check_enabled: false, on_zero_results: ReturnEmpty, ready_state: None, indexes: {}, primary_key: None, on_conflict: {} }), embeddings: [], depends_on: [], invalid_type_action: None, ready_state: OnLoad }], views: [], models: [], dependencies: [], embeddings: [], evals: [], tools: [], runtime: Runtime { results_cache: ResultsCache { enabled: true, cache_max_size: None, item_ttl: None, eviction_policy: None }, dataset_load_parallelism: None, tls: None, tracing: None, telemetry: TelemetryConfig { enabled: true, user_agent_collection: Full, properties: {} }, params: {}, task_history: TaskHistory { enabled: true, captured_output: "none", retention_period: "8h", retention_check_interval: "15m" }, auth: None, cors: CorsConfig { enabled: false, allowed_origins: ["*"] } } }], runtime: Runtime { results_cache: ResultsCache { enabled: true, cache_max_size: None, item_ttl: None, eviction_policy: None }, dataset_load_parallelism: None, tls: None, tracing: None, telemetry: TelemetryConfig { enabled: true, user_agent_collection: Full, properties: {} }, params: {}, task_history: TaskHistory { enabled: true, captured_output: "none", retention_period: "8h", retention_check_interval: "15m" }, auth: None, cors: CorsConfig { enabled: false, allowed_origins: ["*"] } } }), schema: None, invalid_type_action: None, ready_state: OnLoad }
2025-02-07T00:48:23.430433Z  INFO runtime::init::dataset: Dataset taxi_trips_customized registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (arrow), results cache enabled.
2025-02-07T00:48:23.433018Z DEBUG runtime::accelerated_table::refresh: Starting scheduled refresh
2025-02-07T00:48:23.433157Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips_customized
2025-02-07T00:48:23.434113Z  INFO object_store::aws::builder: Using Instance credential provider
2025-02-07T00:48:27.905207Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,964,624 rows (399.41 MiB) for dataset taxi_trips_customized in 4s 472ms.
2025-02-07T00:48:27.905322Z DEBUG runtime::accelerated_table::refresh_task_runner: Refresh task successfully completed for dataset taxi_trips_customized
2025-02-07T00:48:27.905344Z DEBUG runtime::accelerated_table::refresh: Received refresh task completion callback: Ok(())
```

## Specify Spice Docker Image (optional)

Update a `values.yaml`. See [Spice Helm Values](https://spiceai.org/docs/deployment/kubernetes#values) for more deails.

```bash
cat <<EOF > values.yaml
image:
  repository: spiceai/spiceai
  tag: 1.0.2-models
replicaCount: 2

spicepod:
  name: app
  version: v1
  kind: Spicepod

  datasets:
    - from: s3://spiceai-demo-datasets/taxi_trips/2024/
      name: taxi_trips_customized
      description: Demo taxi trips in s3
      params:
        file_format: parquet
      acceleration:
        enabled: true
EOF
```

```bash
helm upgrade spiceai-dev spiceai/spiceai -f values.yaml
```

## Configure Secrets (optional)

Use instructions below to propogate OpenAI API Key secret to Spice. 

Create `spice-openai-api-key` secret

```bash
kubectl create secret generic spice-openai-api-key --from-literal=SPICE_OPENAI_API_KEY="sk-proj-your-api-key"
```

Update a `values.yaml`. See [Spice Helm Values](https://spiceai.org/docs/deployment/kubernetes#values) for more deails.

```bash
cat <<EOF > values.yaml
image:
  repository: spiceai/spiceai
  tag: latest-models

additionalEnv:
  - name: SPICE_OPENAI_API_KEY
    valueFrom:
      secretKeyRef:
        name: spice-openai-api-key
        key: SPICE_OPENAI_API_KEY

spicepod:
  name: app
  version: v1
  kind: Spicepod

  models:
    - from: openai:gpt-4o-mini
      name: gpt-4o
      params:
        spice_tools: auto
        openai_api_key: \${ secrets:SPICE_OPENAI_API_KEY }

  datasets:
    - from: s3://spiceai-demo-datasets/taxi_trips/2024/
      name: taxi_trips_customized
      description: Demo taxi trips in s3
      params:
        file_format: parquet
      acceleration:
        enabled: true
EOF
```

```bash
helm upgrade spiceai-dev spiceai/spiceai -f values.yaml
```

```bash
2025-02-07T01:18:29.987862Z  INFO runtime::init::dataset: Initializing dataset taxi_trips_customized
2025-02-07T01:18:29.987856Z  INFO runtime::init::results_cache: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2025-02-07T01:18:29.987989Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 0.0.0.0:50052
2025-02-07T01:18:29.988057Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 0.0.0.0:9090
2025-02-07T01:18:29.988092Z  INFO runtime::flight: Spice Runtime Flight listening on 0.0.0.0:50051
2025-02-07T01:18:29.988195Z  INFO runtime::init::model: Loading model [gpt-4o] from openai:gpt-4o-mini...
2025-02-07T01:18:29.988530Z  INFO runtime::http: Spice Runtime HTTP listening on 0.0.0.0:8090
2025-02-07T01:18:30.749627Z  INFO runtime::init::dataset: Dataset taxi_trips_customized registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (arrow), results cache enabled.
2025-02-07T01:18:30.751216Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips_customized
2025-02-07T01:18:31.124139Z  INFO runtime::init::model: Model [gpt-4o] deployed, ready for inferencing
2025-02-07T01:18:35.592609Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,964,624 rows (399.41 MiB) for dataset taxi_trips_customized in 4s 841ms.
```

You can now port-forward Spice endpoint and chat with model

```bash
kubectl port-forward deploy/spiceai-dev 8090:8090
```

In a new terminal:

``` bash
spice chat
Using model: gpt-4o
chat> What is the average ride cost
The average ride cost is approximately **$14.52**.

Time: 0.65s (first token 0.48s). Tokens: 1072. Prompt: 1057. Completion: 15 (85.39/s).
```

## Clean up

Uninstall the Spice Helm chart:

```bash
helm uninstall spiceai
```

Delete the Kind cluster:

```bash
kind delete cluster
```
