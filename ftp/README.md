# FTP/SFTP Data Connector

Works with `v1.0+`

Follow these steps to get started with FTP/SFTP as a Data Connector.

## Requirements

- Docker
- Spice.ai runtime installed (see [Getting Started](https://docs.spiceai.org/getting-started))

**Step 1.** Start a local FTP server and a local SFTP server via Docker Compose. Both servers share the same demo csv data.

```bash
git clone https://github.com/spiceai/cookbook # Skip if already cloned
cd cookbook/ftp
make # Start the FTP and SFTP servers
```

The `spicepod.yaml` file loads the same `customers.csv` file two times:

- `customers` uses the FTP server (`ftp://localhost/customers.csv`, port `20021`).
- `customers_sftp` uses the SFTP server (`sftp://localhost/data/customers.csv`, port `20022`).

**Step 2.** Start the Spice runtime.

Set the environment variables `FTP_PASS` and `SFTP_PASS` to the passwords for your FTP and SFTP servers. This can be specified on the command line when running the Spice runtime, or in a `.env` file in the same directory as `spicepod.yaml`.

i.e. to set the passwords for the demo servers in a `.env` file:

```bash
printf "FTP_PASS=123\nSFTP_PASS=123\n" > .env
```

```bash
spice run
```

Output:

```console
2026-10-15T06:01:20.376099Z  INFO runtime::init::dataset: Dataset customers_sftp initializing...
2026-10-15T06:01:20.376181Z  INFO runtime::init::dataset: Dataset customers initializing...
2026-10-15T06:01:20.955893Z  INFO runtime::init::dataset: Dataset customers_sftp registered (sftp://localhost/data/customers.csv), acceleration (cayenne, 10s refresh), results cache enabled. duration_ms=445
2026-10-15T06:01:20.956062Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset customers_sftp
2026-10-15T06:01:21.030279Z  INFO runtime_table::accelerated::refresh_task: Loaded 100 rows (17.94 kiB) for dataset customers_sftp in 74ms.
2026-10-15T06:01:21.085905Z  INFO runtime::init::dataset: Dataset customers registered (ftp://localhost/customers.csv), acceleration (cayenne, 10s refresh), results cache enabled. duration_ms=406
2026-10-15T06:01:21.085927Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset customers
2026-10-15T06:01:21.242553Z  INFO runtime_table::accelerated::refresh_task: Loaded 100 rows (17.94 kiB) for dataset customers in 156ms.
2026-10-15T06:01:21.290845Z  INFO runtime: All components are loaded. Spice runtime is ready!
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

Query the same data through SFTP:

```sql
select count(*) from customers_sftp;
```

Output:

```console
+----------+
| count(*) |
+----------+
| 100      |
+----------+

Time: 0.001904958 seconds. 1 rows.
```

**Step 4.** Exit Spice SQL REPL by running `exit`, and clean up the demo environment:

```bash
make clean
```

[Learn more](https://docs.spiceai.org/components/data-connectors/ftp) about Spice FTP/SFTP Data Connector.
