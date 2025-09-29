# ODBC Data Connector

Follow these steps to get started with ODBC as a Data Connector. This recipe will create an SQLite database, install the SQLite ODBC driver, and connect to SQLite via ODBC with the Spice Runtime.

## Preparation

- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).

## Steps

### Step 1: Install the SQLite ODBC Driver

#### Generic *nix Instructions

Install the [SQLite ODBC driver](https://github.com/softace/sqliteodbc) for your operating system.

On Unix, this requires cloning and compiling the SQLite ODBC driver project. First, install build dependencies:

```bash
sudo apt-get install unixodbc odbcinst sqlite3 libsqlite3-dev
```

Then, clone and compile the SQLite ODBC driver:

```bash
git clone https://github.com/softace/sqliteodbc
cd sqliteodbc
./configure && make
sudo make install
```

Once the driver is installed, configure the ODBC driver profile by editing the `/etc/odbcinst.ini` and adding the SQLite driver:

```ini
[SQLite3]
Driver = /usr/local/lib/libsqlite3odbc.so
```

#### macOS

Install via brew:

```bash
brew install unixodbc sqliteodbc
```

Configure the SQLite driver:
```bash
cat <<EOF >> /opt/homebrew/etc/odbcinst.ini
[SQLite3]
Driver = /opt/homebrew/lib/libsqlite3odbc.so
EOF
```


### Step 2: Setup Data

Setup an SQLite database with some sample data. Use the SQLite CLI to create a database, and run the provided SQL:

```bash
sqlite3 data.sqlite
```

```sql
CREATE TABLE taxi_trips (
  vendorid INT,
  tpep_pickup_datetime DATETIME,
  tpep_dropoff_datetime DATETIME,
  passenger_count INT,
  trip_distance FLOAT,
  ratecodeid INT,
  store_and_fwd_flag CHAR(1),
  pulocationid INT,
  dolocationid INT,
  payment_type INT,
  fare_amount FLOAT,
  extra FLOAT,
  mta_tax FLOAT,
  tip_amount FLOAT,
  tolls_amount FLOAT,
  improvement_surcharge FLOAT,
  total_amount FLOAT,
  congestion_surcharge FLOAT,
  airport_fee FLOAT
);

INSERT INTO taxi_trips VALUES
(2, '2024-01-01 00:57:55', '2024-01-01 01:17:43', 1, 1.72, 1, 'N', 186, 79, 2, 17.7, 1, 0.5, 0, 0, 1, 22.7, 2.5, 0),
(1, '2024-01-01 00:03:00', '2024-01-01 00:09:36', 1, 1.8, 1, 'N', 140, 236, 1, 10.0, 3.5, 0.5, 3.75, 0, 1, 18.75, 2.5, 0),
(1, '2024-01-01 00:17:06', '2024-01-01 00:35:01', 1, 4.7, 1, 'N', 236, 79, 1, 23.3, 3.5, 0.5, 3, 0, 1, 31.3, 2.5, 0);
```

### Step 3: Run Spice

Start Spice inside the cookbook directory, which contains a Spicepod pre-configured to connect to the newly created `taxi_trips` table via ODBC:

```bash
spice run
```

The Spice Runtime should start and become ready:

```console
Spice.ai OSS CLI v1.5.1-build.af574cb4e
2025/07/29 12:02:26 INFO Checking for latest Spice runtime release...
2025/07/29 12:02:26 INFO Spice.ai runtime starting...
2025-07-29T02:02:26.714448Z  INFO spiced: Starting runtime v1.5.1-build.af574cb4e
2025-07-29T02:02:26.714895Z  INFO runtime::init::caching: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2025-07-29T02:02:26.714952Z  INFO runtime::init::caching: Initialized search results cache;
2025-07-29T02:02:27.601396Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-07-29T02:02:27.601397Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2025-07-29T02:02:27.601542Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-07-29T02:02:27.601629Z  INFO runtime::init::dataset: Dataset taxi_trips initializing...
2025-07-29T02:02:27.602927Z  INFO runtime::init::dataset: Dataset taxi_trips registered (odbc:taxi_trips), results cache enabled.
2025-07-29T02:02:27.704384Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

### Step 4: Run a query

In a new terminal, use `spice sql` to run a query:

```sql
SELECT * FROM taxi_trips;
```

Example output:

```console
+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+
| vendorid | tpep_pickup_datetime | tpep_dropoff_datetime | passenger_count | trip_distance | ratecodeid | store_and_fwd_flag | pulocationid | dolocationid | payment_type | fare_amount | extra | mta_tax | tip_amount | tolls_amount | improvement_surcharge | total_amount | congestion_surcharge | airport_fee |
+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+
| 2        | 2024-01-01T00:57:55  | 2024-01-01T01:17:43   | 1               | 1.72          | 1          | N                  | 186          | 79           | 2            | 17.7        | 1.0   | 0.5     | 0.0        | 0.0          | 1.0                   | 22.7         | 2.5                  | 0.0         |
| 1        | 2024-01-01T00:03:00  | 2024-01-01T00:09:36   | 1               | 1.8           | 1          | N                  | 140          | 236          | 1            | 10.0        | 3.5   | 0.5     | 3.75       | 0.0          | 1.0                   | 18.75        | 2.5                  | 0.0         |
| 1        | 2024-01-01T00:17:06  | 2024-01-01T00:35:01   | 1               | 4.7           | 1          | N                  | 236          | 79           | 1            | 23.3        | 3.5   | 0.5     | 3.0        | 0.0          | 1.0                   | 31.3         | 2.5                  | 0.0         |
+----------+----------------------+-----------------------+-----------------+---------------+------------+--------------------+--------------+--------------+--------------+-------------+-------+---------+------------+--------------+-----------------------+--------------+----------------------+-------------+
```