# Spice.ai API Key Authentication

Works with `v1.0+`

Spice supports securing its HTTP, Flight/FlightSQL, and OpenTelemetry endpoints using API keys.

Enable API key authentication with:

```yaml
runtime:
  auth:
    api_key:
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
vary: origin, access-control-request-method, access-control-request-headers
content-length: 12
date: Sun, 13 Sep 2026 12:19:38 GMT

Unauthorized
```

1. Test with the API key:

```shell
curl -H "Content-Type: text/plain" -H "x-api-key: foobar" -XPOST -i http://localhost:8090/v1/sql -d 'SELECT 1'
```

Output:

```shell
$ curl -H "Content-Type: text/plain" -H "x-api-key: foobar" -XPOST -i http://localhost:8090/v1/sql -d 'SELECT 1'
HTTP/1.1 200 OK
content-type: application/json
x-cache: Miss from spiceai
results-cache-status: MISS
results-cache-scope: user
vary: Authorization, X-API-Key, Cookie
vary: origin, access-control-request-method, access-control-request-headers
spice-trace-id: a058f3d2b44f600e05be59eca570fa71
transfer-encoding: chunked
date: Sun, 13 Sep 2026 12:19:44 GMT

[{"Int64(1)":1}]
```

## CLI

1. Start Spice with `spice run`, then open a new terminal
1. Run `spice pods` without an API key

```bash
$ spice pods
ERROR unauthorized: invalid or missing Spice API key. Run `spice login` or set SPICE_API_KEY.
```

1. Now, run `spice pods` with the API key

```bash
$ spice pods --api-key foobar

 NAME     VERSION  DATASETS  MODELS  DEPENDENCIES
 api_key  v1       0         0       0
```

## SQL REPL

1. Start Spice with `spice run`, then open a new terminal
1. Open the SQL REPL with `spice sql`, then attempt a SQL query:

```bash
$ spice sql

sql> select 1;
Authentication Failed: Invalid credentials. Verify credentials and try again.
```

1. Re-open the SQL REPL with the API key and try the query again:

```bash
$ spice sql --api-key foobar

sql> select 1;
+----------+
| Int64(1) |
|   int64  |
+----------+
| 1        |
+----------+

Time: 0.007247375 seconds. 1 rows.
```
