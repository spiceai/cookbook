# Oracle Data Connector

This cookbook demonstrates how to use Spice.ai to connect to and accelerate data from an Oracle database.

The demo includes an Oracle Free database container with sample TPCH data: `lineitem`, `orders`, and `customer`.

## Prerequisites

This recipe requires:

- [Oracle ODPI-C library](https://oracle.github.io/odpi/)
- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)
- [Spice CLI](https://docs.spice.ai/getting-started/install-spice) installed locally

## Getting Started

1. **Clone the repository and navigate to the Oracle cookbook:**

  ```bash
  git clone https://github.com/spiceai/cookbook.git
  cd cookbook/oracle
  ```

2. **Start the Oracle database and load sample data:**

  ```bash
  make
  ```

  Output:

  ```bash
  Starting Oracle database container...
  [+] Running 2/2
  ✔ Network oracle_default     Created                                                                    0.0s 
  ✔ Container oracle-oracle-1  Healthy                                                                   10.7s 
  Oracle database is running at localhost:15211
  Database: FREEPDB1
  Username: scott
  Password: tiger
  ```

3. **Start Spice**

  ```bash
  make spice
  ```

  This will start the Spice runtime which will connect to Oracle and accelerate the TPCH tables locally:

  ```bash
  2025/07/07 13:41:42 INFO Spice.ai runtime starting...
  2025-07-07T20:41:42.882796Z  INFO spiced: Starting runtime v1.5.0-unstable-build.2187f22e7+models
  2025-07-07T20:41:42.884157Z  INFO runtime::init::caching: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
  2025-07-07T20:41:42.884197Z  INFO runtime::init::caching: Initialized search results cache;
  2025-07-07T20:41:43.431896Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
  2025-07-07T20:41:43.431929Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
  2025-07-07T20:41:43.432215Z  INFO runtime::init::dataset: Initializing dataset lineitem
  2025-07-07T20:41:43.432253Z  INFO runtime::init::dataset: Initializing dataset orders
  2025-07-07T20:41:43.432218Z  INFO runtime::init::dataset: Initializing dataset customer
  2025-07-07T20:41:43.432399Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
  2025-07-07T20:41:43.915273Z  INFO runtime::init::dataset: Dataset lineitem registered (oracle:"LINEITEM"), acceleration (arrow), results cache enabled.
  2025-07-07T20:41:43.916361Z  INFO runtime::init::dataset: Dataset orders registered (oracle:"ORDERS"), acceleration (arrow), results cache enabled.
  2025-07-07T20:41:43.916382Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset lineitem
  2025-07-07T20:41:43.917524Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset orders
  2025-07-07T20:41:43.935174Z  INFO runtime::init::dataset: Dataset customer registered (oracle:"CUSTOMER"), acceleration (arrow), results cache enabled.
  2025-07-07T20:41:43.936280Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset customer
  2025-07-07T20:41:43.949015Z  INFO runtime::accelerated_table::refresh_task: Loaded 7 rows (5.56 kiB) for dataset orders in 31ms.
  2025-07-07T20:41:43.949027Z  INFO runtime::accelerated_table::refresh_task: Loaded 27 rows (10.37 kiB) for dataset lineitem in 32ms.
  2025-07-07T20:41:43.950450Z  INFO runtime::accelerated_table::refresh_task: Loaded 7 rows (6.43 kiB) for dataset customer in 14ms.
  2025-07-07T20:41:44.036153Z  INFO runtime: All components are loaded. Spice runtime is ready!
  ```

4. **Run Test Queries**

  Run Spice REPL in another terminal window:

  ```bash
  spice sql
  ```

  Try these queries:

  ```sql
  -- Show available tables
  sql> show tables;
  +---------------+--------------+--------------+------------+
  | table_catalog | table_schema | table_name   | table_type |
  +---------------+--------------+--------------+------------+
  | spice         | runtime      | task_history | BASE TABLE |
  | spice         | public       | orders       | BASE TABLE |
  | spice         | public       | customer     | BASE TABLE |
  | spice         | public       | lineitem     | BASE TABLE |
  +---------------+--------------+--------------+------------+

  Time: 0.018918625 seconds. 4 rows.

  -- Review table schema
  sql> describe lineitem;
  +-----------------+-------------------+-------------+
  | column_name     | data_type         | is_nullable |
  +-----------------+-------------------+-------------+
  | L_ORDERKEY      | Int64             | YES         |
  | L_PARTKEY       | Int64             | YES         |
  | L_SUPPKEY       | Int64             | YES         |
  | L_LINENUMBER    | Int64             | YES         |
  | L_QUANTITY      | Decimal128(15, 2) | YES         |
  | L_EXTENDEDPRICE | Decimal128(15, 2) | YES         |
  | L_DISCOUNT      | Decimal128(15, 2) | YES         |
  | L_TAX           | Decimal128(15, 2) | YES         |
  | L_RETURNFLAG    | Utf8              | YES         |
  | L_LINESTATUS    | Utf8              | YES         |
  | L_SHIPDATE      | Date32            | YES         |
  | L_COMMITDATE    | Date32            | YES         |
  | L_RECEIPTDATE   | Date32            | YES         |
  | L_SHIPINSTRUCT  | Utf8              | YES         |
  | L_SHIPMODE      | Utf8              | YES         |
  | L_COMMENT       | Utf8              | YES         |
  +-----------------+-------------------+-------------+

  Time: 0.005356291 seconds. 16 rows.

  -- Calculate total sales by customer
  SELECT c.C_NAME, SUM(l.L_EXTENDEDPRICE) as total_sales
  FROM customer c
  JOIN orders o ON c.C_CUSTKEY = o.O_CUSTKEY
  JOIN lineitem l ON o.O_ORDERKEY = l.L_ORDERKEY
  GROUP BY c.C_NAME
  ORDER BY total_sales DESC;
  ```

## Clean Up

To stop and remove the Docker containers:

```bash
make clean
```
