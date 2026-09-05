# HTTP Data Connector

Works with `v2.0+`

The HTTP(s) data connector enables querying data from HTTP(s) endpoints such as REST APIs. The connector supports dynamic query construction and data refresh through SQL-based filtering, making it ideal for integrating external APIs and web-hosted datasets into your Spice application.

This recipe demonstrates how to use the HTTP connector with the [TVMaze API](https://www.tvmaze.com/api) to query TV show information using dynamic endpoint routing.

## Pre-requisites

- The latest version of Spice. [Install Spice](https://docs.spiceai.org/getting-started)
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
      allowed_request_paths: "/shows/**,/search/people"
      request_query_filters: enabled
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
 INFO Spice.ai runtime starting...
2026-09-05T21:54:00.787858Z  INFO spiced: Starting runtime v2.2.1+models.metal
...
2026-09-05T21:54:00.793801Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2026-09-05T21:54:00.793829Z  INFO runtime::init::caching: Initialized search results cache; max size: 128.00 MiB, item ttl: 1s, engine: Moka
2026-09-05T21:54:00.793839Z  INFO runtime::init::caching: Initialized embeddings cache; max size: 128.00 MiB, item ttl: 1s, engine: Moka
2026-09-05T21:54:00.795378Z  INFO runtime::init::task_history: Task history enabled: retention_period=28800s, retention_check_interval=900s
2026-09-05T21:54:00.795492Z  INFO runtime::init::dataset: Loading datasets: 2 tasks dispatched, 0 skipped at accelerator init (of 2 total; localpod datasets may be chained).
2026-09-05T21:54:00.795515Z  INFO runtime::init::dataset: Dataset tvmaze initializing...
2026-09-05T21:54:00.795825Z  INFO runtime::init::dataset: Dataset products initializing...
2026-09-05T21:54:00.799774Z  INFO runtime::init::dataset: Dataset products registered (https://dummyjson.com/products), results cache enabled. duration_ms=0
2026-09-05T21:54:00.799774Z  INFO runtime::init::dataset: Dataset tvmaze registered (https://api.tvmaze.com), results cache enabled. duration_ms=0
2026-09-05T21:54:00.901507Z  INFO runtime: All components are loaded. Spice runtime is ready!
2026-09-05T21:54:00.994991Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2026-09-05T21:54:00.995358Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
```

The elided lines report the CPU and memory budgets the runtime derives for this host, so their values differ from machine to machine.

**Step 3.** Run `spice sql` in a new terminal to start an interactive SQL query session.

For more information on using `spice sql`, see the [CLI reference](https://docs.spiceai.org/cli/reference/sql).

**Step 4.** Execute queries to explore the TVMaze API:

### Query a specific show by ID

```sql
SELECT * FROM tvmaze WHERE request_path = '/shows/169';
```

This queries the Breaking Bad show details. The `content` column contains the full JSON response:

```console
+--------------+---------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------+
| request_path | request_query | request_body | content                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | response_status | response_headers                                                                                                                                                                                                                                                    | _fetched_at         |
+--------------+---------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------+
| /shows/169   |               |              | {"id":169,"url":"https://www.tvmaze.com/shows/169/breaking-bad","name":"Breaking Bad","type":"Scripted","language":"English","genres":["Drama","Crime","Thriller"],"status":"Ended","runtime":60,"averageRuntime":60,"premiered":"2008-01-20","ended":"2019-10-11","officialSite":"http://www.amc.com/shows/breaking-bad","schedule":{"time":"22:00","days":["Sunday"]},"rating":{"average":9.2},"weight":99,"network":{"id":20,"name":"AMC","country":{"name":"United States","code":"US","timezone":"America/New_York"},"officialSite":null},"webChannel":null,"dvdCountry":null,"externals":{"tvrage":18164,"thetvdb":81189,"imdb":"tt0903747"},"image":{"medium":"https://static.tvmaze.com/uploads/images/medium_portrait/501/1253519.jpg","original":"https://static.tvmaze.com/uploads/images/original_untouched/501/1253519.jpg"},"summary":"<p><b>Breaking Bad</b> follows protagonist Walter White, a chemistry teacher who lives in New Mexico with his wife and teenage son who has cerebral palsy. White is diagnosed with Stage III cancer and given a prognosis of two years left to live. With a new sense of fearlessness based on his medical prognosis, and a desire to secure his family's financial security, White chooses to enter a dangerous world of drugs and crime and ascends to power in this world. The series explores how a fatal diagnosis such as White's releases a typical man from the daily concerns and constraints of normal society and follows his transformation from mild family man to a kingpin of the drug trade.</p>","updated":1769198028,"_links":{"self":{"href":"https://api.tvmaze.com/shows/169"},"previousepisode":{"href":"https://api.tvmaze.com/episodes/2007806","name":"El Camino: A Breaking Bad Movie"}}} | 200             | {server: nginx/1.24.0 (Ubuntu), date: Mon, 09 Mar 2026 08:45:28 GMT, content-type: application/json; charset=UTF-8, transfer-encoding: chunked, connection: keep-alive, vary: Accept-Encoding, access-control-allow-origin: *, cache-control: public, max-age=3600} | 2026-03-09T08:45:28 |
+--------------+---------------+--------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------+

Time: 0.108725875 seconds. 1 rows.
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

This executes two separate API calls (one for each query parameter) and combines the results — 10 results per search term, for 20 rows in total:

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

Time: 0.336182833 seconds. 20 rows.
```

## Advanced Usage

### Processing JSON Responses

TVMaze API responses contain nested JSON. Use [JSON functions](https://docs.spiceai.org/reference/sql/json) to extract specific fields:

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

## Pagination

The HTTP connector supports automatic pagination for REST APIs that return data across multiple pages. This recipe includes a second dataset that demonstrates query-parameter pagination with the [DummyJSON Products API](https://dummyjson.com/docs/products).

### Configuration

The `products` dataset in `spicepod.yaml` uses query-parameter pagination:

```yaml
datasets:
  - from: https://dummyjson.com/products
    name: products
    params:
      pagination: enabled
      pagination_query_params: "skip={offset}&limit={limit}"
      pagination_page_size: "30"
      pagination_data_pointer: "/products"
      pagination_max_pages: "10"
```

- **`pagination: enabled`** — Turns on pagination.
- **`pagination_query_params`** — Template with `{offset}` and `{limit}` variables. Spice expands these automatically for each page (`skip=0&limit=30`, `skip=30&limit=30`, …).
- **`pagination_page_size`** — Number of items per page. Also determines when to stop: if a page returns fewer rows than this value, pagination is complete.
- **`pagination_max_pages`** — Safety limit on the number of pages to fetch.

### Querying Paginated Data

Count all products fetched across pages:

```sql
SELECT count(*) FROM products;
```

```console
+----------+
| count(*) |
|   int64  |
+----------+
| 194      |
+----------+
```

All 194 products are returned transparently — Spice fetches 7 pages (30 items each, except the last page with 14) and combines them into a single result set.

Inspect products and observe how `request_query` changes as rows span pages:

```sql
SELECT request_query,
       json_get_str(content, 'title') AS title,
       json_get_float(content, 'price') AS price
FROM products
LIMIT 35;
```

```console
+------------------+-------------------------------------------+---------+
|   request_query  |                   title                   |  price  |
|      varchar     |                  varchar                  | float64 |
+------------------+-------------------------------------------+---------+
| skip=0&limit=30  | Essence Mascara Lash Princess             | 9.99    |
| skip=0&limit=30  | Eyeshadow Palette with Mirror             | 19.99   |
| skip=0&limit=30  | Powder Canister                           | 14.99   |
| skip=0&limit=30  | Red Lipstick                              | 12.99   |
| skip=0&limit=30  | Red Nail Polish                           | 8.99    |
| ...              | ...                                       | ...     |
| skip=0&limit=30  | Kiwi                                      | 2.49    |
| skip=30&limit=30 | Lemon                                     | 0.79    |
| skip=30&limit=30 | Milk                                      | 3.49    |
| skip=30&limit=30 | Mulberry                                  | 4.99    |
| skip=30&limit=30 | Nescafe Coffee                            | 7.99    |
| skip=30&limit=30 | Potatoes                                  | 2.29    |
+------------------+-------------------------------------------+---------+
```

The first 30 rows come from page 1 (`skip=0&limit=30`), then rows from page 2 (`skip=30&limit=30`) follow automatically.

For the full pagination parameter reference, see the [HTTP Data Connector documentation](https://docs.spiceai.org/components/data-connectors/https#pagination-parameters).

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
      http_headers: "Authorization:Bearer ${secrets:TVMAZE_TOKEN}"
```

### Multiple Custom Headers

Combine multiple headers for complex authentication requirements:

```yaml
datasets:
  - from: https://api.tvmaze.com/premium
    name: tvmaze_premium
    params:
      file_format: json
      http_headers: "Authorization:Bearer ${secrets:TOKEN},X-API-Key:${secrets:API_KEY},Accept:application/json"
```

Always use [secret stores](https://docs.spiceai.org/components/secret-stores) to manage sensitive credentials in production.

## Learn More

- [HTTP(s) Data Connector Documentation](https://docs.spiceai.org/components/data-connectors/https)
- [Secret Stores](https://docs.spiceai.org/components/secret-stores)
- [TVMaze API Documentation](https://www.tvmaze.com/api)
