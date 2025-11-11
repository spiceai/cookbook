# HTTP Data Connector

The HTTP(s) data connector enables querying data from HTTP(s) endpoints such as REST APIs. The connector supports dynamic query construction and data refresh through SQL-based filtering, making it ideal for integrating external APIs and web-hosted datasets into your Spice application.

This recipe demonstrates how to use the HTTP connector with the [TVMaze API](https://www.tvmaze.com/api) to query TV show information using dynamic endpoint routing.

## Pre-requisites

- The latest version of Spice. [Install Spice](https://docs.spiceai.org/getting-started/installation)
- An HTTP(s) endpoint that returns data in a [supported file format](https://docs.spiceai.org/components/data-connectors#object-store-file-formats)

## Configuration

The HTTP connector supports two configuration approaches:

1. **Direct URL to a file**: A complete URL pointing to a specific file (e.g., `https://github.com/user/repo/raw/main/data.csv`)
2. **Base domain/path**: A base URL combined with special metadata fields to construct requests dynamically

This recipe uses approach #2 with the TVMaze API to demonstrate dynamic endpoint routing.

### Special Metadata Fields

The HTTP connector supports three special metadata fields for dynamic request construction:

| Field Name      | Description                                                                    | Example              |
| --------------- | ------------------------------------------------------------------------------ | -------------------- |
| `request_path`  | URL path to append to the base URL                                             | `/shows/169`         |
| `request_query` | Query parameters to append to the URL (formatted as `key1=value1&key2=value2`) | `q=michael&limit=10` |
| `request_body`  | Request body for POST/PUT requests (triggers POST method when provided)        | `{"name":"example"}` |

These fields allow you to query different endpoints and pass parameters dynamically through SQL queries.

## Example: Querying TVMaze API for TV Shows

**Step 1.** Review the `spicepod.yaml` configuration file in this directory.

The configuration uses a base URL approach, allowing dynamic routing to different API endpoints:

```yaml
datasets:
  - from: https://api.tvmaze.com
    name: tvmaze
    params:
      file_format: json
      client_timeout: 30s
```

- **`from`**: The base URL for the TVMaze API. The connector will append paths and query parameters to this base.
- **`file_format`**: Specifies that the API returns JSON data.
- **`client_timeout`**: Maximum time to wait for a response (default: 30s).

The HTTP connector automatically exposes special metadata fields (`request_path`, `request_query`, `request_body`) for dynamic routing.

For more configuration options, see the [HTTP Data Connector documentation](https://docs.spiceai.org/components/data-connectors/https).

### Common HTTP Connector Parameters

| Parameter                | Description                                                               | Default     |
| ------------------------ | ------------------------------------------------------------------------- | ----------- |
| `file_format`            | Format of data returned (json, csv, parquet, etc.)                        | Auto-detect |
| `client_timeout`         | Maximum time to wait for a response                                       | `30s`       |
| `connect_timeout`        | Timeout for establishing connections                                      | `10s`       |
| `http_username`          | Username for HTTP Basic authentication                                    | None        |
| `http_password`          | Password for HTTP Basic authentication (use secret stores for production) | None        |
| `http_headers`           | Custom HTTP headers as comma-separated `key:value` pairs                  | None        |
| `pool_max_idle_per_host` | Maximum idle connections to keep alive per host                           | `10`        |
| `max_retries`            | Maximum retry attempts for failed requests                                | `3`         |
| `retry_backoff_method`   | Retry strategy: `fibonacci`, `linear`, or `exponential`                   | `fibonacci` |

**Step 2.** Run the Spice runtime with `spice run` from this directory.

```bash
cd http
spice run
```

Example output:

```console
2025/11/09 14:51:05 INFO Checking for latest Spice runtime release...
2025/11/09 14:51:05 INFO Spice.ai runtime starting...
2025-11-09T22:51:05.790767Z  INFO spiced: Starting runtime v1.9.0-unstable-build.521d6438f+models.metal
2025-11-09T22:51:05.792981Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s
2025-11-09T22:51:05.793020Z  INFO runtime::init::caching: Initialized search results cache; max size: 128.00 MiB, item ttl: 1s
2025-11-09T22:51:05.793031Z  INFO runtime::init::caching: Initialized embeddings cache; max size: 128.00 MiB, item ttl: 1s
2025-11-09T22:51:06.136639Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2025-11-09T22:51:06.137090Z  INFO runtime::init::task_history: Task history enabled: retention_period=28800s, retention_check_interval=900s
2025-11-09T22:51:06.137446Z  INFO runtime::init::dataset: Dataset tvmaze initializing...
2025-11-09T22:51:06.137756Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-11-09T22:51:06.336540Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-11-09T22:51:06.367725Z  INFO runtime::init::dataset: Dataset tvmaze registered (https://api.tvmaze.com), results cache enabled.
2025-11-09T22:51:06.671311Z  INFO runtime::management: Connected to Spice Cloud for management and monitoring
2025-11-09T22:51:06.774002Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

**Step 3.** Run `spice sql` in a new terminal to start an interactive SQL query session.

For more information on using `spice sql`, see the [CLI reference](https://docs.spiceai.org/cli/reference/sql).

**Step 4.** Execute queries to explore the TVMaze API:

### Query a specific show by ID

```sql
SELECT * FROM tvmaze WHERE request_path = '/shows/169';
```

This queries the Breaking Bad show details. The `content` column contains the full JSON response:

```console
+---------------+--------------+---------------+------------------------------------------+
| request_path  | request_query| request_body  | content                                  |
+---------------+--------------+---------------+------------------------------------------+
| /shows/169    |              |               | {"id":169,"url":"https://www.tvmaze.com/|
|            |        |       | shows/169/breaking-bad","name":"Breaking |
|            |        |       | Bad","type":"Scripted","language":       |
|            |        |       | "English","genres":["Drama","Crime",     |
|            |        |       | "Thriller"],"status":"Ended",...}        |
+------------+--------+-------+------------------------------------------+

Time: 0.16491975 seconds. 1 rows.
```

### Search for people using query parameters

```sql
SELECT * FROM tvmaze
WHERE request_path = '/search/people'
  AND request_query = 'q=michael';
```

This searches the TVMaze API for people named "michael". Returns 10 results by default.

### Query multiple search terms

```sql
SELECT * FROM tvmaze
WHERE request_path = '/search/people'
  AND request_query IN ('q=michael', 'q=luke');
```

This executes two separate API calls (one for each query parameter) and combines the results:

```console
+----------------+---------------+--------------+------------------------------------+
| request_path   | request_query | request_body | content                            |
+----------------+---------------+--------------+------------------------------------+
| /search/people | q=michael     |              | {"score":0.70710677,"person":{...}}|
| /search/people | q=michael     |              | {"score":0.70710677,"person":{...}}|
| ...            | ...           | ...          | ...                                |
| /search/people | q=luke        |              | {"score":0.5,"person":{...}}       |
| /search/people | q=luke        |              | {"score":0.5,"person":{...}}       |
+----------------+---------------+--------------+------------------------------------+

Time: 0.336182833 seconds. 40 rows.
```

## Advanced Usage

### Processing JSON Responses

TVMaze API responses contain nested JSON. Use [JSON functions](/docs/reference/sql/json) to extract specific fields:

```sql
-- Extract show details from JSON response
SELECT
  json_get_str(content, 'name') as show_name,
  json_get_str(content, 'type') as show_type,
  json_get_int(content, 'runtime') as runtime_minutes,
  json_get_str(content, 'status') as status
FROM tvmaze
WHERE request_path = '/shows/169';
```

For deeply nested fields, chain JSON functions:

```sql
-- Extract network information from nested JSON
SELECT
  json_get_str(content, 'name') as show_name,
  json_get_str(json_get(content, 'network'), 'name') as network_name,
  json_get_str(json_get(json_get(content, 'network'), 'country'), 'code') as country_code
FROM tvmaze
WHERE request_path = '/shows/82';
```

## Dynamic HTTP Connector Features

The HTTP connector provides powerful dynamic capabilities through special metadata fields that allow you to construct HTTP requests dynamically via SQL queries.

### How It Works

When you query the dataset with filters on special metadata fields, Spice dynamically constructs HTTP requests:

```sql
-- GET request to a specific path
WHERE request_path = '/shows/169'
  → GET https://api.tvmaze.com/shows/169

-- GET request with query parameters
WHERE request_path = '/search/people' AND request_query = 'q=michael'
  → GET https://api.tvmaze.com/search/people?q=michael

-- POST request with body (automatically uses POST when request_body is provided)
WHERE request_path = '/api/endpoint' AND request_body = '{"key":"value"}'
  → POST https://api.tvmaze.com/api/endpoint (with JSON body)
```

Multiple values in metadata fields trigger multiple API calls that are automatically combined in the result set.

### Examples with TVMaze API

## Use Cases

The HTTP connector is ideal for:

- **REST API Integration**: Query any REST API that returns JSON, CSV, or Parquet data
- **Dynamic API Exploration**: Access multiple endpoints from a single dataset configuration using special metadata fields
- **Search and Filter APIs**: Leverage query parameters for filtering, searching, and pagination
- **Incremental Data Loading**: Fetch only new or updated records using dynamic filters
- **Static Data Files**: Access data files hosted on web servers or cloud storage
- **Third-Party Data Services**: Integrate external data sources without ETL pipelines
- **IoT and Sensor Data**: Pull real-time data from IoT devices with HTTP interfaces
- **Federated Queries**: Combine data from multiple HTTP sources in a single SQL query

## Timeouts and Retries

The HTTP connector provides granular control over timeouts and automatic retry behavior:

### Timeouts

Configure timeouts for different stages of the HTTP request:

```yaml
datasets:
  - from: https://api.tvmaze.com
    name: tvmaze
    params:
      file_format: json
      client_timeout: 60s # Total time for request-response cycle
      connect_timeout: 15s # Time to establish connection
```

- **`client_timeout`**: Maximum time to wait for a complete HTTP response (default: 30s)
- **`connect_timeout`**: Maximum time to establish a connection (default: 10s)

### Connection Pooling

Improve performance by configuring connection pooling:

```yaml
datasets:
  - from: https://api.tvmaze.com
    name: tvmaze
    params:
      file_format: json
      pool_max_idle_per_host: 20 # Max idle connections per host (default: 10)
      pool_idle_timeout: 120 # How long to keep idle connections (default: 90s)
```

### Retries

The HTTP connector automatically retries failed requests with configurable retry behavior:

```yaml
datasets:
  - from: https://api.tvmaze.com
    name: tvmaze
    params:
      file_format: json
      max_retries: 5 # Number of retry attempts (default: 3)
      retry_backoff_method: exponential # fibonacci, linear, or exponential (default: fibonacci)
      retry_max_duration: 2m # Total time limit for all retries
      retry_jitter: 0.5 # Randomization to prevent thundering herd (default: 0.3)
```

The connector automatically retries transient failures such as network errors and 5xx server errors.

## Authentication

The HTTP connector supports multiple authentication methods. While the TVMaze API is public and doesn't require authentication, here are examples for APIs that do:

### HTTP Basic Authentication

For APIs requiring basic authentication:

```yaml
datasets:
  - from: https://api.tvmaze.com/premium
    name: tvmaze_premium
    params:
      file_format: json
      http_username: ${secrets:TVMAZE_USERNAME}
      http_password: ${secrets:TVMAZE_PASSWORD}
```

### Bearer Token / API Key Authentication

Use custom headers for bearer tokens or API keys:

```yaml
datasets:
  - from: https://api.tvmaze.com/premium
    name: tvmaze_premium
    params:
      file_format: json
      http_headers: 'Authorization:Bearer ${secrets:TVMAZE_TOKEN}'
```

### Multiple Custom Headers

Combine multiple headers for complex authentication requirements:

```yaml
datasets:
  - from: https://api.tvmaze.com/premium
    name: tvmaze_premium
    params:
      file_format: json
      http_headers: 'Authorization:Bearer ${secrets:TOKEN},X-API-Key:${secrets:API_KEY},Accept:application/json'
```

Always use [secret stores](https://docs.spiceai.org/components/secret-stores) to manage sensitive credentials in production.

## Learn More

- [HTTP(s) Data Connector Documentation](https://docs.spiceai.org/components/data-connectors/https)
- [Secret Stores](https://docs.spiceai.org/components/secret-stores)
- [TVMaze API Documentation](https://www.tvmaze.com/api)
