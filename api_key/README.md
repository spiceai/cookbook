# Spice.ai API Key Authentication

Spice supports securing its HTTP, Flight/FlightSQL, and OpenTelemetry endpoints using API keys.

Enable API key authentication with:

```yaml
runtime:
  auth:
    api-key:
      enabled: true
      keys:
        - ${ env:API_KEY }
```

Create a `.env` file in the same directory as `spicepod.yaml` to set an API key that will be pulled from the environment:

```shell
API_KEY=foobar
```

## HTTP

1. Start Spice with `spice run`, then open a new terminal
1. To test without an API key, run:

  ```shell
  curl -XPOST -i http://localhost:8090/v1/sql -d 'SELECT 1'
  ```

  Expected response:

  ```shell
  $ curl -XPOST -i http://localhost:8090/v1/sql -d 'SELECT 1'
  HTTP/1.1 401 Unauthorized
  content-length: 12
  date: Thu, 07 Nov 2024 01:52:00 GMT

  Unauthorized
  ```

1. Test with the API key:

  ```shell
  curl -H "x-api-key: foobar" -XPOST -i http://localhost:8090/v1/sql -d 'SELECT 1'
  ```

  Output:

  ```shell
  curl -H "x-api-key: foobar" -XPOST -i http://localhost:8090/v1/sql -d 'SELECT 1'
  HTTP/1.1 200 OK
  content-type: text/plain; charset=utf-8
  x-cache: Miss from spiceai
  content-length: 16
  date: Thu, 07 Nov 2024 01:53:20 GMT

  [{"Int64(1)":1}]
  ```

## CLI

1. Start Spice with `spice run`, then open a new terminal
1. Run `spice status` without an API key

  ```bash
  $ spice status
  2024/11/07 17:29:48 ERROR getting spiced status error="error fetching runtime information: Unauthorized"
  ```

1. Now, run `spice status` with the API key

  ```bash
  $ spice status --api-key foobar

  NAME          ENDPOINT        STATUS
  http          127.0.0.1:8090  Ready
  flight        127.0.0.1:50051 Ready
  metrics       127.0.0.1:9090  Ready
  opentelemetry 127.0.0.1:50052 Ready
  ```

## SQL REPL

1. Start Spice with `spice run`, then open a new terminal
1. Open the SQL REPL with `spice sql`, then attempt a SQL query:

  ```bash
  $ spice sql

  sql> select 1;
  Authentication Error Access denied. Invalid credentials.
  ```

1. Re-open the SQL REPL with the API key and try the query again:

  ```bash
  $ spice sql --api-key foobar

  sql> select 1;
  +----------+
  | Int64(1) |
  +----------+
  | 1        |
  +----------+

  Time: 0.007247375 seconds. 1 rows.
  ```
