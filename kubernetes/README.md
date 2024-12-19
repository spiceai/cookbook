# Running Spice.ai in Kubernetes Recipe

**Step 1.** (Optional) Start a local [`kind`](https://kind.sigs.k8s.io/) cluster:

```bash
go install sigs.k8s.io/kind@v0.22.0
kind create cluster
```

See [kind installation](https://kind.sigs.k8s.io/docs/user/quick-start/#installation) for other installation options.

**Step 2.** Install Spice in your Kubernetes cluster using Helm:

```bash
helm repo add spiceai https://helm.spiceai.org
helm install spiceai spiceai/spiceai
```

Output:

```bash
NAME: spiceai
LAST DEPLOYED: Wed Nov 27 13:55:43 2024
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None
```

**Step 3.** Verify that the Spice pods are running:

```bash
kubectl get pods
kubectl logs deploy/spiceai
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
kubectl exec -it deploy/spiceai -- spiced --repl
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

**Step 6.** Create a `values.yaml` file to configure the Spice deployment:

```bash
cat <<EOF > values.yaml
spicepod:
  name: app
  version: v1beta1
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
helm upgrade spiceai spiceai/spiceai -f values.yaml
```

Output:

```bash
Release "spiceai" has been upgraded. Happy Helming!
NAME: spiceai
LAST DEPLOYED: Wed Nov 27 13:57:35 2024
NAMESPACE: default
STATUS: deployed
REVISION: 2
TEST SUITE: None
```

**Step 8.** Rerun the Spice SQL REPL

```bash
kubectl exec -it deploy/spiceai -- spiced --repl
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

## Clean up

Uninstall the Spice Helm chart:

```bash
helm uninstall spiceai
```

Delete the Kind cluster:

```bash
kind delete cluster
```
