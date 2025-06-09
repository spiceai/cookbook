# FTP/SFTP Data Connector

Follow these steps to get started with FTP/SFTP as a Data Connector.

## Requirements

- Docker
- Spice.ai runtime installed (see [Getting Started](https://docs.spiceai.org/getting-started))

**Step 1.** Start a local FTP server preloaded with demo csv data via Docker Compose.

```bash
git clone https://github.com/spiceai/cookbook # Skip if already cloned
cd cookbook/ftp
make # Start the FTP server
```

**Step 2.** Start the Spice runtime.

Set the environment variable `FTP_PASS`/`SFTP_PASS` to the password for your FTP server. This can be specified on the command line when running the Spice runtime, or in a `.env` file in the same directory as `spicepod.yaml`.

i.e. to set the password in a `.env` file:

```bash
echo "FTP_PASS=123" > .env
```

```bash
spice run
```

Output:

```console
2025-06-09T17:59:19.959978Z  INFO spiced: Starting runtime v1.4.0-rc.1+models
2025-06-09T17:59:19.961855Z  INFO runtime::init::caching: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2025-06-09T17:59:19.962011Z  INFO runtime::init::caching: Initialized search results cache;
2025-06-09T17:59:21.486798Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-06-09T17:59:21.486881Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2025-06-09T17:59:21.491284Z  INFO runtime::init::dataset: Initializing dataset customers
2025-06-09T17:59:21.492025Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-06-09T17:59:21.633945Z  INFO runtime::init::dataset: Dataset customers registered (ftp://localhost/customers.csv), acceleration (arrow, 10s refresh), results cache enabled.
2025-06-09T17:59:21.635123Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset customers
2025-06-09T17:59:21.707071Z  INFO runtime::accelerated_table::refresh_task: Loaded 100 rows (23.05 kiB) for dataset customers in 71ms.
2025-06-09T17:59:21.735570Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

See the [datasets reference](https://docs.spiceai.org/reference/spicepod/datasets) for more dataset configuration options.

**Step 3.** Run `spice sql` in a new terminal to start an interactive SQL query session against the Spice runtime.

```bash
spice sql
```

```sql
-- Query data from loaded customers.csv
select * from customers limit 5;
```

Output:

```console
+-----------+--------------------+--------------------------------+-------------+-----------------+-----------+--------------+-------------------------------------------------------------------------------------------------------+
| c_custkey | c_name             | c_address                      | c_nationkey | c_phone         | c_acctbal | c_mktsegment | c_comment                                                                                             |
+-----------+--------------------+--------------------------------+-------------+-----------------+-----------+--------------+-------------------------------------------------------------------------------------------------------+
| 1         | Customer#000000001 | j5JsirBM9PsCy0O1m              | 15          | 25-989-741-2988 | 711.56    | BUILDING     | y final requests wake slyly quickly special accounts. blithely                                        |
| 2         | Customer#000000002 | 487LW1dovn6Q4dMVymKwwLE9OKf3QG | 13          | 23-768-687-3665 | 121.65    | AUTOMOBILE   | y carefully regular foxes. slyly regular requests about the bli                                       |
| 3         | Customer#000000003 | fkRGN8nY4pkE                   | 1           | 11-719-748-3364 | 7498.12   | AUTOMOBILE   | fully. carefully silent instructions sleep alongside of the slyly regular asymptotes. quickly regular |
| 4         | Customer#000000004 | 4u58h fqkyE                    | 4           | 14-128-190-5944 | 2866.83   | MACHINERY    |  sublate. fluffily even instructions are about th                                                     |
| 5         | Customer#000000005 | hwBtxkoBF qSW4KrIk5U 2B1AU7H   | 3           | 13-750-942-6364 | 794.47    | HOUSEHOLD    | equests haggle furiously against the pending packa                                                    |
+-----------+--------------------+--------------------------------+-------------+-----------------+-----------+--------------+-------------------------------------------------------------------------------------------------------+

Time: 0.011731833 seconds. 5 rows.
```

**Step 4.** Clean up the demo environment:

```bash
make clean
```

[Learn more](https://docs.spiceai.org/data-connectors/ftp) about Spice FTP/SFTP Data Connector.
