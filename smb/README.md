# SMB Data Connector

Works with `v1.11+`

This recipe demonstrates how to configure a Spice dataset to connect to SMB (Server Message Block) network shares and query data files using federated SQL queries.

## Prerequisites

- An SMB/CIFS file server (Windows Server, Samba, NAS device, or Azure Files)
- Network access to the SMB server (port 445 by default)
- User credentials with read access to the target share
- Spice.ai runtime ([Getting Started](https://docs.spiceai.org/getting-started))

---

## Step 1. Clone this cookbook repo locally

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/smb
```

---

## Step 2. Set Up an SMB Server (Optional)

If you don't have an existing SMB server, you can start one locally using Docker with Samba:

```bash
docker run -d --name samba \
  -p 445:445 \
  -v $(pwd)/data:/share \
  -e USERID=1000 \
  -e GROUPID=1000 \
  dperson/samba \
  -u "testuser;testpass" \
  -s "data;/share;yes;no;no;testuser"
```

This creates a share named `data` accessible with username `testuser` and password `testpass`.

---

## Step 3. Add Sample Data

Create a `data` directory with sample Parquet files:

```bash
mkdir -p data
```

You can copy any Parquet or CSV files into the `data` directory, or use the Spice CLI to generate sample data.

---

## Step 4. Configure Spice Credentials

Update the `.env` file with your SMB credentials:

```env
SMB_USER=testuser
SMB_PASS=testpass
```

---

## Step 5. Start the Spice Runtime

```bash
spice run
```

If the configuration is correct, you should see output similar to:

```console
INFO runtime::init::dataset: Dataset sales initializing...
INFO runtime::init::dataset: Dataset sales registered (smb://localhost/data/), acceleration (none), results cache enabled.
```

---

## Step 6. Query the SMB Share with the Spice SQL REPL

```bash
spice sql
```

To show tables:

```sql
SHOW TABLES;
```

To query your data:

```sql
SELECT * FROM sales LIMIT 10;
```

---

## Configuration Options

### Connection Parameters

| Parameter Name              | Description                                                       | Default |
| --------------------------- | ----------------------------------------------------------------- | ------- |
| `file_format`               | Required when connecting to a directory. Parquet, CSV, JSON, etc. | -       |
| `smb_user`                  | Username for SMB authentication.                                  | -       |
| `smb_pass`                  | Password for SMB authentication.                                  | -       |
| `smb_port`                  | SMB server port.                                                  | `445`   |
| `client_timeout`            | Connection timeout duration. E.g. `30s`, `1m`.                    | -       |
| `hive_partitioning_enabled` | Enable Hive-style partitioning from folder structure.             | `false` |

### Supported File Formats

- Parquet
- CSV
- JSON
- NDJSON

---

## Examples

### Basic Connection

Connect to a Windows file share with credentials:

```yaml
datasets:
  - from: smb://fileserver.corp.local/shared/analytics/
    name: analytics
    params:
      file_format: parquet
      smb_user: ${secrets:smb_user}
      smb_pass: ${secrets:smb_pass}
```

### Domain Authentication

For Windows domain environments, include the domain in the username:

```yaml
datasets:
  - from: smb://fileserver/data/reports/
    name: reports
    params:
      file_format: csv
      csv_has_header: true
      smb_user: DOMAIN\username
      smb_pass: ${secrets:smb_pass}
```

The domain can be specified as `DOMAIN\user` or `user@domain`.

### Reading a Single File

When pointing to a specific file, the format is inferred from the file extension:

```yaml
datasets:
  - from: smb://nas.local/backups/database_export.parquet
    name: database_export
    params:
      smb_user: ${secrets:smb_user}
      smb_pass: ${secrets:smb_pass}
```

### Connection with Timeout

Configure a timeout for slow or unreliable network connections:

```yaml
datasets:
  - from: smb://remote-server.example.com/data/
    name: remote_data
    params:
      file_format: parquet
      smb_user: ${secrets:smb_user}
      smb_pass: ${secrets:smb_pass}
      client_timeout: 60s
```

### Custom Port Configuration

Connect to SMB servers running on non-standard ports:

```yaml
datasets:
  - from: smb://custom-server.local/share/
    name: custom_data
    params:
      file_format: parquet
      smb_port: 4450
      smb_user: ${secrets:smb_user}
      smb_pass: ${secrets:smb_pass}
```

### Hive Partitioning

Enable Hive-style partitioning to automatically extract partition columns from the folder structure:

```yaml
datasets:
  - from: smb://datalake.corp.local/warehouse/events/
    name: events
    params:
      file_format: parquet
      smb_user: ${secrets:smb_user}
      smb_pass: ${secrets:smb_pass}
      hive_partitioning_enabled: true
```

Given a folder structure like:

```text
/events/
  region=us/
    year=2024/
      data.parquet
  region=eu/
    year=2024/
      data.parquet
```

Queries can filter on partition columns:

```sql
SELECT * FROM events WHERE region = 'us' AND year = '2024';
```

### Multiple Shares from One Server

Load different datasets from multiple shares on the same server:

```yaml
datasets:
  - from: smb://fileserver/sales/
    name: sales
    params:
      file_format: parquet
      smb_user: ${secrets:smb_user}
      smb_pass: ${secrets:smb_pass}

  - from: smb://fileserver/inventory/
    name: inventory
    params:
      file_format: csv
      smb_user: ${secrets:smb_user}
      smb_pass: ${secrets:smb_pass}
```

### Accelerated Dataset

Enable local acceleration for faster repeated queries:

```yaml
datasets:
  - from: smb://archive.corp.local/historical/
    name: historical_data
    params:
      file_format: parquet
      smb_user: ${secrets:smb_user}
      smb_pass: ${secrets:smb_pass}
    acceleration:
      enabled: true
      engine: duckdb
      refresh_check_interval: 1h
```

Acceleration is recommended for frequently queried data, as SMB operations involve network round-trips for directory listing and file reads.

---

## Supported SMB Versions

The SMB connector supports SMB protocols 2.0, 2.1, 3.0, and 3.1.1, and is compatible with:

- Windows Server file shares
- Samba servers (Linux/Unix)
- NAS devices (Synology, QNAP, etc.)
- Azure Files

---

## Limitations

- **Read-only**: The connector does not support write operations (INSERT, UPDATE, DELETE)
- **Authentication**: Only username/password authentication is supported. Kerberos and NTLM ticket-based authentication are not available
- **Network access**: Direct network access to the SMB server is required; proxy connections are not supported
- **Firewall**: The firewall must permit SMB traffic (port 445 by default)

---

## Troubleshooting

### Connection Timeouts

If connections frequently timeout, increase the `client_timeout` value:

```yaml
params:
  client_timeout: 120s
```

Verify network connectivity to the server and check that firewall rules permit port 445.

### Authentication Failures

Common causes of authentication failures:

- **Domain not specified**: For domain-joined servers, include the domain: `DOMAIN\username` or `username@domain`
- **Incorrect credentials**: Verify username and password are correctly stored in your secret store
- **Permission denied**: Ensure the user has read access to the share and files
- **Account locked**: Check if the SMB account is not locked on the server

### Share Access Errors

If you receive "share not found" errors:

- Verify the share name is correct (share names are case-insensitive on Windows)
- Ensure the share exists and is accessible from the network where Spice is running
- Check firewall rules: SMB uses TCP port 445
- Confirm the user has permission to access the share

### Enable Debug Logging

For additional troubleshooting information, enable debug logging:

```bash
SPICED_LOG="runtime=debug,spice_cloud=debug" spice run
```

---

## Step 7. Cleanup

To stop and remove the Samba container:

```bash
docker stop samba
docker rm samba
```

---

## Additional Resources

- [SMB Data Connector Documentation](https://docs.spiceai.org/components/data-connectors/smb)
- [File Formats Documentation](https://docs.spiceai.org/components/data-connectors/index#file-formats)
- [Secret Stores Documentation](https://docs.spiceai.org/components/secret-stores)
- [Data Acceleration](https://docs.spiceai.org/features/data-acceleration)
