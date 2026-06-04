# Unity Catalog Connector

Works with `v2.0+`

The Unity Catalog Connector makes querying tables in a Unity Catalog with Spice simple.

Note: This recipe applies to the [open-source version of Unity Catalog](https://www.unitycatalog.io/). To get started with the Databricks Unity Catalog Connector, see the [Databricks Unity Catalog Connector recipe](../databricks/README.md).

## Prerequisites

- Docker and Docker Compose installed.
- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).

## Step 1. Start Unity Catalog

Start a local Unity Catalog instance with sample data using Docker Compose:

```bash
docker compose up -d
```

This starts:
- **Unity Catalog server** on `http://localhost:8081` — metadata catalog
- **MinIO** on `http://localhost:9000` (console: `http://localhost:9001`) — S3-compatible object store for Delta Lake tables
- **Unity Catalog UI** on `http://localhost:3000` — browse the catalog
- **Seed container** — populates the catalog with sample Delta Lake tables in MinIO

The seed container creates a `unity.samples` schema with realistic tables:
- **customers** (100 rows) — customer dimension with name, email, segment, location
- **products** (50 rows) — product catalog with categories, pricing, stock
- **orders** (500 rows) — order fact table with status, payment method
- **order_items** (~1500 rows) — line items linking orders to products

You can browse the catalog in the UI at [http://localhost:3000](http://localhost:3000) and the MinIO console at [http://localhost:9001](http://localhost:9001) (credentials: `minio` / `minio123`).

## Step 2. Start the Spice runtime

The included `spicepod.yaml` is pre-configured to connect to the local Unity Catalog and MinIO:

```bash
spice run
```

## Step 3. Query the data

```bash
spice sql
```

```sql
show tables;
```

```console
+---------------+--------------+--------------+------------+
| table_catalog | table_schema |  table_name  | table_type |
|    varchar    |    varchar   |    varchar   |   varchar  |
+---------------+--------------+--------------+------------+
| uc            | samples      | products     | BASE TABLE |
| uc            | samples      | customers    | BASE TABLE |
| uc            | samples      | orders       | BASE TABLE |
| uc            | samples      | order_items  | BASE TABLE |
| spice         | runtime      | task_history | BASE TABLE |
+---------------+--------------+--------------+------------+
```

```sql
SELECT * FROM uc.samples.customers LIMIT 5;
```

```console
+-------------+------------+-----------+-----------------------------+----------------+-----------+---------+---------+--------------+
| customer_id | first_name | last_name |            email            |     segment    |    city   |  state  | country | created_date |
|    int32    |   varchar  |  varchar  |           varchar           |     varchar    |  varchar  | varchar | varchar |     date     |
+-------------+------------+-----------+-----------------------------+----------------+-----------+---------+---------+--------------+
| 1           | Emma       | Brown     | emma.brown1@example.com     | Small Business | New York  | NY      | US      | 2019-04-05   |
| 2           | Liam       | Brown     | liam.brown2@example.com     | Consumer       | Toronto   | ON      | CA      | 2022-07-02   |
| 3           | James      | Williams  | james.williams3@example.com | Corporate      | Houston   | TX      | US      | 2022-10-01   |
| 4           | Sarah      | Miller    | sarah.miller4@example.com   | Enterprise     | Vancouver | BC      | CA      | 2019-08-19   |
| 5           | David      | Smith     | david.smith5@example.com    | Corporate      | Sydney    | NSW     | AU      | 2023-07-11   |
+-------------+------------+-----------+-----------------------------+----------------+-----------+---------+---------+--------------+
```

```sql
-- Top customers by order count
SELECT c.first_name, c.last_name, c.segment, COUNT(o.order_id) AS order_count
FROM uc.samples.customers c
JOIN uc.samples.orders o ON c.customer_id = o.customer_id
GROUP BY c.first_name, c.last_name, c.segment
ORDER BY order_count DESC
LIMIT 10;
```

```console
+------------+-----------+----------------+-------------+
| first_name | last_name |     segment    | order_count |
|   varchar  |  varchar  |     varchar    |    int64    |
+------------+-----------+----------------+-------------+
| Emma       | Thompson  | Corporate      | 12          |
| David      | Brown     | Consumer       | 12          |
| Barbara    | Anderson  | Enterprise     | 10          |
| Sarah      | Miller    | Enterprise     | 10          |
| Ava        | Brown     | Consumer       | 9           |
| William    | Moore     | Enterprise     | 9           |
| David      | Jones     | Small Business | 9           |
| Karen      | Hernandez | Enterprise     | 9           |
| Oliver     | White     | Corporate      | 9           |
| Oliver     | Lee       | Small Business | 8           |
+------------+-----------+----------------+-------------+
```

```sql
-- Revenue by product category
SELECT p.category, SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
FROM uc.samples.order_items oi
JOIN uc.samples.products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY revenue DESC;
```

```console
+-----------------+--------------------+
|     category    |       revenue      |
|     varchar     |       float64      |
+-----------------+--------------------+
| Office Supplies | 1160538.9765       |
| Software        | 1149024.566        |
| Electronics     | 1094495.8760000002 |
| Furniture       | 1089822.738        |
| Peripherals     | 1053972.9875       |
+-----------------+--------------------+
```

## Step 4. Clean up

Stop all services:

```bash
docker compose down -v
```

## How It Works

Unity Catalog is a **metadata-only catalog** — it stores table schemas and their storage locations, but not the actual data. The data lives in Delta Lake format on an S3-compatible object store (MinIO in this recipe).

The `spicepod.yaml` configuration:

```yaml
version: v2
kind: Spicepod
name: unity-catalog-demo

catalogs:
  - from: unity_catalog:http://localhost:8081/api/2.1/unity-catalog/catalogs/unity
    name: uc
    include:
      - samples.*
    params:
      unity_catalog_aws_access_key_id: minio
      unity_catalog_aws_secret_access_key: minio123
      unity_catalog_aws_region: us-east-1
      unity_catalog_aws_endpoint: http://localhost:9000
      unity_catalog_aws_allow_http: "true"
```

Spice connects to Unity Catalog to discover table metadata, then reads the actual Delta Lake data directly from MinIO using the S3 credentials.

Visit the documentation for more information configuring the [Unity Catalog Connector](https://docs.spiceai.org/components/catalogs/unity-catalog).
