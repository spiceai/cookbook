# Running Spice.ai in Kubernetes

Works with `v1.0+`

**Step 1.** (Optional) Start a local [`kind`](https://kind.sigs.k8s.io/) cluster:

```bash
go install sigs.k8s.io/kind@v0.30.0
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
2024-11-27T21:55:48.116548Z  INFO runtime::http: Spice Runtime HTTP listening on 0.0.0.0:8090
2024-11-27T21:55:48.116578Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
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
+---------------+--------------+--------------+------------+
| table_catalog | table_schema |  table_name  | table_type |
|    varchar    |    varchar   |    varchar   |   varchar  |
+---------------+--------------+--------------+------------+
| spice         | runtime      | task_history | BASE TABLE |
| spice         | runtime      | metrics      | BASE TABLE |
+---------------+--------------+--------------+------------+
```

**Step 6.** Create a `values.yaml` file to configure the Spice deployment. See [Spice Helm Values](https://spiceai.org/docs/deployment/kubernetes/helm) for more details.

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
| table_catalog | table_schema |       table_name      | table_type |
|    varchar    |    varchar   |        varchar        |   varchar  |
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
+--------------+-----------------------+---------------+-------------+
| table_schema |      column_name      |   data_type   | is_nullable |
|    varchar   |        varchar        |    varchar    |   varchar   |
+--------------+-----------------------+---------------+-------------+
| public       | VendorID              | Int32         | YES         |
| public       | tpep_pickup_datetime  | Timestamp(µs) | YES         |
| public       | tpep_dropoff_datetime | Timestamp(µs) | YES         |
| public       | passenger_count       | Int64         | YES         |
| public       | trip_distance         | Float64       | YES         |
| public       | RatecodeID            | Int64         | YES         |
| public       | store_and_fwd_flag    | Utf8          | YES         |
| public       | PULocationID          | Int32         | YES         |
| public       | DOLocationID          | Int32         | YES         |
| public       | payment_type          | Int64         | YES         |
| public       | fare_amount           | Float64       | YES         |
| public       | extra                 | Float64       | YES         |
| public       | mta_tax               | Float64       | YES         |
| public       | tip_amount            | Float64       | YES         |
| public       | tolls_amount          | Float64       | YES         |
| public       | improvement_surcharge | Float64       | YES         |
| public       | total_amount          | Float64       | YES         |
| public       | congestion_surcharge  | Float64       | YES         |
| public       | Airport_fee           | Float64       | YES         |
+--------------+-----------------------+---------------+-------------+

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

## Clean up

Uninstall the Spice Helm chart:

```bash
helm uninstall spiceai-dev
```

Delete the Kind cluster:

```bash
kind delete cluster
```
