# Live Orders Analytics with Apache Kafka Data Connector

In this recipe, you'll learn how to combine real-time data streaming from Kafka with other datasets using federated queries. The setup uses Apache Kafka with a test producer generating order events to the `orders_events` topic. The Spice runtime consumes these events, keeping an accelerated `orders` dataset updated in real time, enabling you to join this live data with other sources (such as S3 TPC-H benchmark data) for powerful analytics.

## Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) are installed.
- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).

## How to run

Clone this cookbook repo locally and navigate to the `kafka` directory:

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/kafka
```

Start the Docker Compose stack, which includes a Kafka broker via the `apache/kafka:latest` Docker image and a test message producer.

```shell
docker compose up -d
```

Output:

```shell
[+] Running 5/5
 ✔ Network kafka_default          Created                                                                                                                                                                                           0.0s 
 ✔ Container broker               Healthy                                                                                                                                                                                          11.8s 
 ✔ Container kafka-ui             Started                                                                                                                                                                                          11.3s 
 ✔ Container kafka-topic-setup-1  Started                                                                                                                                                                                          11.3s 
 ✔ Container kafka-producer-1     Started   
```

Navigate to <http://localhost:8080/ui/clusters/local/all-topics> to see the Apache Kafka console and the `orders_events` topic configured.

This `spicepod.yaml` shows the config needed to configure Spice to connect to this Kafka topic:

```yaml
version: v1
kind: Spicepod
name: kafka-demo

datasets:
  - from: kafka:orders_events
    name: orders
    params:
      kafka_bootstrap_servers: localhost:9092
      kafka_security_protocol: PLAINTEXT
    acceleration:
      enabled: true
      engine: duckdb
      mode: file
      refresh_mode: append
```

Ensure the current directory is `kafka`, and start the Spice runtime:

```bash
spice run
```

Observe that Spice loads data from the configured Kafka topic into the `orders` dataset

```bash
2025-08-24T05:06:40.084870Z  INFO spiced: Starting runtime v1.6.0-unstable-build.d7fadb4c2-dev+models
2025-08-24T05:06:40.086387Z  INFO runtime::init::caching: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2025-08-24T05:06:40.086548Z  INFO runtime::init::caching: Initialized search results cache;
2025-08-24T05:06:40.525189Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-08-24T05:06:40.534247Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2025-08-24T05:06:40.538475Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-08-24T05:06:40.575784Z  INFO runtime::init::dataset: Dataset nation initializing...
2025-08-24T05:06:40.575784Z  INFO runtime::init::dataset: Dataset supplier initializing...
2025-08-24T05:06:40.575821Z  INFO runtime::init::dataset: Dataset customer initializing...
2025-08-24T05:06:40.575839Z  INFO runtime::init::dataset: Dataset orders initializing...
2025-08-24T05:06:40.628259Z  INFO runtime::init::dataset: Dataset orders registered (kafka:orders_events), acceleration (duckdb:file, append), results cache enabled.
2025-08-24T05:06:41.527790Z  INFO runtime::init::dataset: Dataset nation registered (s3://spiceai-demo-datasets/tpch/nation/), acceleration (duckdb:file), results cache enabled.
2025-08-24T05:06:41.531264Z  INFO runtime::init::dataset: Dataset customer registered (s3://spiceai-demo-datasets/tpch/customer/), acceleration (duckdb:file), results cache enabled.
2025-08-24T05:06:41.531332Z  INFO runtime::init::dataset: Dataset supplier registered (s3://spiceai-demo-datasets/tpch/supplier/), acceleration (duckdb:file), results cache enabled.
2025-08-24T05:06:54.138084Z DEBUG runtime::accelerated_table::refresh_task::changes: Inserting data row for orders
2025-08-24T05:06:54.167452Z DEBUG runtime::accelerated_table::refresh_task::changes: Inserting data row for orders
...
```

Run `spice sql` in a separate terminal to query the data

```sql
select * from orders limit 5;
```

Output:

```shell
+--------------------------------------+---------+---------+---------+----------+------------+--------------------+
| order_id                             | custkey | partkey | suppkey | quantity | unit_price | order_ts           |
+--------------------------------------+---------+---------+---------+----------+------------+--------------------+
| 445cb50a-9393-463b-8103-87757875b386 | 693     | 457     | 227     | 24       | 643.33     | 1756011628.4742422 |
| 1791e046-fda3-4584-be39-3fc3eec455d3 | 659     | 426     | 29      | 75       | 917.22     | 1756011633.4823549 |
| 45f019c6-afc5-4d95-b435-7c5f178f6fba | 89      | 15      | 215     | 25       | 483.02     | 1756011637.4861696 |
| 96801e6d-bb3d-41e6-91f4-9f1e5edbba76 | 283     | 144     | 261     | 57       | 251.09     | 1756011641.490414  |
| c3631e4f-2ef7-4739-96db-d5b595636ba7 | 351     | 384     | 184     | 55       | 245.47     | 1756011643.4923162 |
+--------------------------------------+---------+---------+---------+----------+------------+--------------------+
```

The demo Spicepod configuration also contains TPC-H benchmark data from S3—specifically, the `customer`, `nation`, and `supplier` tables. These can be joined with real-time orders for advanced analytics using federated queries.

## Federated Query Example

Enrich real-time orders with S3 TPC-H dimensions: Join the live orders stream with customer, nation, and supplier dimension tables stored on S3 to return enriched rows (customer name, country, supplier).

```sql
SELECT
  TO_TIMESTAMP(o.order_ts) as timestampt,
  c.c_name,
  n.n_name AS customer_nation,
  s.s_name,
  o.quantity,
  o.unit_price,
  (o.quantity * o.unit_price) AS order_revenue
FROM orders o
JOIN customer c ON o.custkey = c.c_custkey
JOIN nation n   ON c.c_nationkey = n.n_nationkey
JOIN supplier s ON o.suppkey = s.s_suppkey
ORDER BY o.order_ts DESC
LIMIT 5;
```

Output:

```shell
+-------------------------------+--------------------+-----------------+--------------------+----------+------------+--------------------+
| timestampt                    | c_name             | customer_nation | s_name             | quantity | unit_price | order_revenue      |
+-------------------------------+--------------------+-----------------+--------------------+----------+------------+--------------------+
| 1970-01-01T00:00:01.756008276 | Customer#000000032 | MOROCCO         | Supplier#000000035 | 59       | 599.66     | 35379.939999999995 |
| 1970-01-01T00:00:01.756008275 | Customer#000000462 | VIETNAM         | Supplier#000000084 | 18       | 337.26     | 6070.68            |
| 1970-01-01T00:00:01.756008274 | Customer#000000995 | JORDAN          | Supplier#000000048 | 50       | 198.77     | 9938.5             |
| 1970-01-01T00:00:01.756008273 | Customer#000000493 | MOZAMBIQUE      | Supplier#000000127 | 17       | 321.59     | 5467.03            |
| 1970-01-01T00:00:01.756008272 | Customer#000000042 | ETHIOPIA        | Supplier#000000075 | 21       | 440.78     | 9256.38            |
+-------------------------------+--------------------+-----------------+--------------------+----------+------------+--------------------+
```

## KPI Example: Last-Hour Orders Snapshot

Compute last-hour orders KPI snapshot: Computes rolling 1-hour KPIs from the orders stream—total orders, revenue, average items per order, average unit price, and distinct customers/suppliers.

```sql
WITH recent AS (
  SELECT *
  FROM orders
  WHERE TO_TIMESTAMP(order_ts) >= CAST(NOW() AS TIMESTAMP) - INTERVAL '1' HOUR
)
SELECT
  COUNT(*)                      AS orders_1h,
  SUM(quantity * unit_price)    AS revenue_1h,
  AVG(quantity)                 AS avg_items_per_order,
  AVG(unit_price)               AS avg_unit_price,
  COUNT(DISTINCT custkey)       AS distinct_customers,
  COUNT(DISTINCT suppkey)       AS distinct_suppliers
FROM recent;
```

Output:

```shell
+-----------+-------------------+---------------------+--------------------+--------------------+--------------------+
| orders_1h | revenue_1h        | avg_items_per_order | avg_unit_price     | distinct_customers | distinct_suppliers |
+-----------+-------------------+---------------------+--------------------+--------------------+--------------------+
| 617       | 15247398.74000002 | 50.3614262560778    | 488.44943273905983 | 450                | 260                |
+-----------+-------------------+---------------------+--------------------+--------------------+--------------------+
```

## Clean up

To stop and remove the Docker containers/volumes that were created, run:

`make clean`

If you don't have the `make` command available, you can run the following command:

```bash
docker compose down -v
```

## Learn more

[Kafka Data Connector Documentation](https://spiceai.org/docs/components/data-connectors/kafka)  
[Data Acceleration](https://spiceai.org/docs/features/data-acceleration)
