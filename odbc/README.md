# ODBC Data Connector

Works with `v1.0+`

Follow these steps to get started with ODBC as a Data Connector. This recipe installs the MariaDB Connector/ODBC driver, runs a MySQL server in Docker with a sample `users` table, and connects to it via ODBC with the Spice Runtime.

> **Why MariaDB Connector/ODBC?**
> Spice (via the `odbc-api` library) declares **ODBC 3.8** to the Driver Manager when it opens a connection. Older drivers — notably the popular SQLite ODBC driver (`libsqlite3odbc`), which only implements **ODBC 3.0** — cannot honor that and the Driver Manager logs a warning:
>
> ```
> WARN odbc_api::handles::logging: State: 01000, Native error: 0, Message: [unixODBC][Driver Manager]Driver does not support the requested version
> ```
>
> The connection still works (the driver negotiates down), but the warning is noise. MariaDB Connector/ODBC is a modern **ODBC 3.8** driver, so the version handshake is clean and no warning is emitted. It speaks the MySQL protocol, so the same driver works against both **MySQL** and **MariaDB** servers.

## Preparation

- **Spice with ODBC support**: ODBC support is not included in the released binaries. See [Building Spice with ODBC](https://spiceai.org/docs/components/data-connectors/odbc#building-spice-with-odbc) for instructions on how to build Spice with ODBC support.
- **Docker**: used to run the MySQL server. No local database install is required.

## Steps

### Step 1: Install the MariaDB Connector/ODBC driver

The ODBC driver must be installed on the **host** where Spice runs — Spice loads it in-process and connects over TCP to the MySQL server (which we will run in Docker in Step 2).

#### macOS

Install the ODBC Driver Manager and the MariaDB ODBC driver via brew:

```bash
brew install unixodbc mariadb-connector-odbc
```

Register the driver with the Driver Manager using `odbcinst` (the official unixODBC tool — it writes to the correct `odbcinst.ini` and is safe to re-run, unlike appending to the file by hand):

```bash
odbcinst -i -d -r <<EOF
[MariaDB]
Description = MariaDB Connector/ODBC (ODBC 3.8)
Driver = /opt/homebrew/opt/mariadb-connector-odbc/lib/mariadb/libmaodbc.dylib
EOF
```

Confirm it registered with `odbcinst -q -d` (you should see `[MariaDB]`).

#### Generic \*nix Instructions

On Debian/Ubuntu:

```bash
sudo apt-get install unixodbc odbcinst odbc-mariadb
```

On Fedora:

```bash
sudo dnf install unixODBC mariadb-connector-odbc
```

The distro packages usually register the driver automatically. Confirm with:

```bash
odbcinst -q -d
```

If `[MariaDB]` is not listed, register it with `odbcinst` (adjust the `Driver` path to match your distribution — e.g. `/usr/lib/x86_64-linux-gnu/odbc/libmaodbc.so`):

```bash
odbcinst -i -d -r <<EOF
[MariaDB]
Description = MariaDB Connector/ODBC (ODBC 3.8)
Driver = /usr/lib/x86_64-linux-gnu/odbc/libmaodbc.so
EOF
```

### Step 2: Run MySQL in Docker and load sample data

Start a MySQL server in a container. The environment variables create the `spice_demo` database and a `spice` user automatically:

```bash
docker run -d --name spice-mysql \
  -e MYSQL_ROOT_PASSWORD=root_pw \
  -e MYSQL_DATABASE=spice_demo \
  -e MYSQL_USER=spice \
  -e MYSQL_PASSWORD=spice_pw \
  -p 3306:3306 \
  mysql:9
```

Wait a few seconds for the server to become ready:

```bash
until docker exec spice-mysql mysqladmin ping -uspice -pspice_pw -h127.0.0.1 --silent; do sleep 2; done
```

Load the sample data:

```bash
docker exec -i spice-mysql mysql -uspice -pspice_pw spice_demo <<'SQL'
CREATE TABLE users (
  id INT,
  username VARCHAR(64),
  email VARCHAR(128),
  signup_date DATE,
  active BOOLEAN
);

INSERT INTO users VALUES
(1, 'alice_j', 'alice@example.com', '2024-01-15', 1),
(2, 'bob_s',   'bob@example.com',   '2024-02-03', 1),
(3, 'carol_w', 'carol@example.com', '2024-03-22', 0);
SQL
```

The `spicepod.yaml` in this directory connects with the following ODBC connection string:

```
DRIVER={MariaDB};SERVER=127.0.0.1;PORT=3306;DATABASE=spice_demo;UID=spice;PWD=spice_pw;SSLMODE=REQUIRED;
```

> `SSLMODE=REQUIRED` is needed because MySQL 8+/9+ default to the `caching_sha2_password` authentication plugin, which requires a secure channel for the initial authentication.

### Step 3: Run Spice

Start Spice inside the cookbook directory, which contains a Spicepod pre-configured to connect to the `users` table via ODBC:

```bash
spice run
```

The Spice Runtime should start and become ready — note that there is **no ODBC version warning**:

```console
2026-06-30T23:57:36.290458Z  INFO spiced: Starting runtime v2.1.0
2026-06-30T23:57:36.383106Z  INFO runtime::init::dataset: Dataset users initializing...
2026-06-30T23:57:36.410556Z  INFO runtime::init::dataset: Dataset users registered (odbc:users), results cache enabled.
2026-06-30T23:57:36.515305Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

### Step 4: Run a query

In a new terminal, use `spice sql` to run a query:

```sql
SELECT * FROM users;
```

Example output:

```console
+----+----------+-------------------+-------------+--------+
| id | username | email             | signup_date | active |
+----+----------+-------------------+-------------+--------+
| 1  | alice_j  | alice@example.com | 2024-01-15  | 1      |
| 2  | bob_s    | bob@example.com   | 2024-02-03  | 1      |
| 3  | carol_w  | carol@example.com | 2024-03-22  | 0      |
+----+----------+-------------------+-------------+--------+
```

### Cleanup

When you're done, stop and remove the container:

```bash
docker rm -f spice-mysql
```

> **Note on `ORDER BY`:** Spice pushes `ORDER BY` down to the source as `ORDER BY ... NULLS LAST`. MySQL does not support that ANSI syntax and will reject the query, whereas MariaDB servers accept it. If you are on MySQL and need ordering, sort on the Spice side (e.g. by materializing into an accelerator) or omit pushed-down `ORDER BY`. This is a SQL-dialect detail and is unrelated to the ODBC version handshake above.
