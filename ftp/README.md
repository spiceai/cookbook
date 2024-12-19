# FTP/SFTP Data Connector Recipe

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

```bash
# In a new terminal
cd cookbook/ftp
spice run
```

See the [datasets reference](https://docs.spiceai.org/reference/spicepod/datasets) for more dataset configuration options.

Set the environment variable `FTP_PASS`/`SFTP_PASS` to the password for your FTP server. This can be specified on the command line when running the Spice runtime, or in a `.env` file in the same directory as `spicepod.yaml`.

i.e. to set the password in a `.env` file:

```bash
echo "FTP_PASS=123" > .env
```

**Step 3.** Run `spice sql` in a new terminal to start an interactive SQL query session against the Spice runtime.

```bash
spice sql
```

```sql
-- Query data from loaded customers.csv
select * from customers;
```

**Step 4.** Clean up the demo environment:

```bash
make clean
```

[Learn more](https://docs.spiceai.org/data-connectors/ftp) about Spice FTP/SFTP Data Connector.
