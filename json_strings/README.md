# JSON strings

Works with `v1.0+`

This recipe demonstrates how to work with JSON strings with Spice. A JSON string represents a JSON object serialized into a string format.

JSON string manipulation in Spice is based on [datafusion-functions-json](https://github.com/datafusion-contrib/datafusion-functions-json) which parses strings into JSON objects and provides the following functionality:

### Supported Functions

- `json_contains(json: str, *keys: str | int) -> bool`  
  Returns `true` if a JSON string contains a specific key (used for the `?` operator).

- `json_get(json: str, *keys: str | int) -> JsonUnion`  
  Retrieves a value from a JSON string based on its "path".

- `json_get_str(json: str, *keys: str | int) -> str`  
  Retrieves a string value from a JSON string based on its "path".

- `json_get_int(json: str, *keys: str | int) -> int`  
  Retrieves an integer value from a JSON string based on its "path".

- `json_get_float(json: str, *keys: str | int) -> float`  
  Retrieves a float value from a JSON string based on its "path".

- `json_get_bool(json: str, *keys: str | int) -> bool`  
  Retrieves a boolean value from a JSON string based on its "path".

- `json_get_json(json: str, *keys: str | int) -> str`  
  Retrieves a nested raw JSON string from a JSON string based on its "path".

- `json_as_text(json: str, *keys: str | int) -> str`  
  Retrieves any value from a JSON string based on its "path" and represents it as a string (used for the `->>` operator).

- `json_length(json: str, *keys: str | int) -> int`  
  Returns the length of a JSON string or array.

### Supported Operators

- `->` operator  
  Alias for `json_get`.

- `->>` operator  
  Alias for `json_as_text`.

- `?` operator  
  Alias for `json_contains`.

## Prerequisites

- Ensure the Spice CLI is installed. Follow the [Getting Started](https://docs.spiceai.org/getting-started) guide if you haven't done it yet.

- Clone repository and navigate to the `JSON strings` recipe:

  ```shell
  git clone https://github.com/spiceai/cookbook
  cd cookbook/json_strings
  ```

## Run Spice

```shell
spice run
```

Result:

```console
 INFO Spice.ai runtime starting...
2026-08-01T12:22:17.791116Z  INFO spiced: Starting runtime v2.1.2+models
2026-08-01T12:22:17.792634Z  INFO runtime::init::caching: Initialized sql results cache; max size: 128.00 MiB, item ttl: 1s, hashing algorithm: XXH3, encoding: none
2026-08-01T12:22:17.792680Z  INFO runtime::init::caching: Initialized search results cache; max size: 128.00 MiB, item ttl: 1s, engine: Moka
2026-08-01T12:22:17.792697Z  INFO runtime::init::caching: Initialized embeddings cache; max size: 128.00 MiB, item ttl: 1s, engine: Moka
2026-08-01T12:22:17.793678Z  INFO runtime::datafusion: Cayenne global encode-concurrency budget active (caps aggregate write-encode shards across all tables) encode_budget=6
2026-08-01T12:22:17.793719Z  INFO runtime::datafusion: Cayenne dynamic-tuning memory budget active (cgroup-aware) memory_budget=8589934592
2026-08-01T12:22:17.794005Z  INFO runtime::init::task_history: Task history enabled: retention_period=28800s, retention_check_interval=900s
2026-08-01T12:22:17.794127Z  INFO runtime::init::dataset: Loading datasets: 1 tasks dispatched, 0 skipped at accelerator init (of 1 total; localpod datasets may be chained).
2026-08-01T12:22:17.794149Z  INFO runtime::init::dataset: Dataset products initializing...
2026-08-01T12:22:17.794478Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2026-08-01T12:22:17.794970Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2026-08-01T12:22:17.796959Z  INFO runtime::init::dataset: Dataset products registered (file://tshirts.csv), acceleration (arrow), results cache enabled. duration_ms=0
2026-08-01T12:22:17.797065Z  INFO runtime::datafusion: Initializing view products_with_color
2026-08-01T12:22:17.798404Z  INFO runtime_table::accelerated::refresh_task: Loading data for dataset products
2026-08-01T12:22:17.799379Z  INFO runtime_table::accelerated::refresh_task: Loaded 8 rows (3.46 kiB) for dataset products in 0s.
2026-08-01T12:22:18.721572Z  INFO runtime::datafusion: View products_with_color registered.
2026-08-01T12:22:18.820636Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

Run `spice sql` in another window and review the `products` dataset structure. You will observe that the `products.properties` field represents JSON data stored as a string (Utf8).

```console
sql> describe products;
+-------------+-----------+-------------+
| column_name | data_type | is_nullable |
|   varchar   |  varchar  |   varchar   |
+-------------+-----------+-------------+
| id          | Int64     | YES         |
| name        | Utf8      | YES         |
| properties  | Utf8      | YES         |
+-------------+-----------+-------------+
```

```console
sql> select * from products;
+-------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   id  |           name          |                                                                         properties                                                                         |
| int64 |         varchar         |                                                                           varchar                                                                          |
+-------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 1     | Ink Fusion T-Shirt      | {"size": ["S", "M", "L", "XL"], "color": "white", "inventory": {"stock": {"S": 12, "M": 20, "L": 10, "XL": 4}, "locations": ["warehouse_1", "store_1"]}}   |
| 2     | ThreadVerse T-Shirt     | {"size": ["S", "M", "L", "XL"], "color": "black", "inventory": {"stock": {"S": 7, "M": 15, "L": 9, "XL": 3}, "locations": ["warehouse_2", "store_2"]}}     |
| 3     | Design Dynamo T-Shirt   | {"size": ["M", "L", "XL"], "color": "blue", "inventory": {"stock": {"M": 10, "L": 7, "XL": 2}, "locations": ["warehouse_3", "store_3"]}}                   |
| 4     | Artistry Apex T-Shirt   | {"size": ["M", "L", "XL"], "color": "red", "inventory": {"stock": {"M": 10, "L": 8, "XL": 5}, "locations": ["warehouse_1", "store_4"]}}                    |
| 5     | Graphite Glow T-Shirt   | {"size": ["S", "M", "L", "XL"], "color": "gray", "inventory": {"stock": {"S": 10, "M": 8, "L": 6, "XL": 3}, "locations": ["warehouse_2", "store_5"]}}      |
| 6     | Sunburst Shine T-Shirt  | {"size": ["S", "M", "L", "XL"], "color": "yellow", "inventory": {"stock": {"S": 20, "M": 25, "L": 15, "XL": 10}, "locations": ["warehouse_1", "store_6"]}} |
| 7     | Oceanic Opal T-Shirt    | {"size": ["S", "M", "L", "XL"], "color": "teal", "inventory": {"stock": {"S": 5, "M": 7, "L": 4, "XL": 2}, "locations": ["warehouse_3", "store_7"]}}       |
| 8     | Crimson Cascade T-Shirt | {"size": ["S", "M", "L", "XL"], "color": "maroon", "inventory": {"stock": {"S": 8, "M": 12, "L": 9, "XL": 3}, "locations": ["warehouse_4", "store_8"]}}    |
+-------+-------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
```

## Working with JSON strings

Use the `->>` operator to retrieve a JSON property as text. For example, to extract the product colors from the JSON data in the `properties` column:

```console
sql> select name, properties->>'color' color from products;
+-------------------------+---------+
|           name          |  color  |
|         varchar         | varchar |
+-------------------------+---------+
| Ink Fusion T-Shirt      | white   |
| ThreadVerse T-Shirt     | black   |
| Design Dynamo T-Shirt   | blue    |
| Artistry Apex T-Shirt   | red     |
| Graphite Glow T-Shirt   | gray    |
| Sunburst Shine T-Shirt  | yellow  |
| Oceanic Opal T-Shirt    | teal    |
| Crimson Cascade T-Shirt | maroon  |
+-------------------------+---------+
```

Use the `->` operator to retrieve a JSON property as a JSON object.

```console
sql> select name, properties->'inventory' from products;
+-------------------------+----------------------------------------------------------------------------------------------------+
|           name          |                                      properties -> 'inventory'                                     |
|         varchar         |                                                union                                               |
+-------------------------+----------------------------------------------------------------------------------------------------+
| Ink Fusion T-Shirt      | {object={"stock": {"S": 12, "M": 20, "L": 10, "XL": 4}, "locations": ["warehouse_1", "store_1"]}}  |
| ThreadVerse T-Shirt     | {object={"stock": {"S": 7, "M": 15, "L": 9, "XL": 3}, "locations": ["warehouse_2", "store_2"]}}    |
| Design Dynamo T-Shirt   | {object={"stock": {"M": 10, "L": 7, "XL": 2}, "locations": ["warehouse_3", "store_3"]}}            |
| Artistry Apex T-Shirt   | {object={"stock": {"M": 10, "L": 8, "XL": 5}, "locations": ["warehouse_1", "store_4"]}}            |
| Graphite Glow T-Shirt   | {object={"stock": {"S": 10, "M": 8, "L": 6, "XL": 3}, "locations": ["warehouse_2", "store_5"]}}    |
| Sunburst Shine T-Shirt  | {object={"stock": {"S": 20, "M": 25, "L": 15, "XL": 10}, "locations": ["warehouse_1", "store_6"]}} |
| Oceanic Opal T-Shirt    | {object={"stock": {"S": 5, "M": 7, "L": 4, "XL": 2}, "locations": ["warehouse_3", "store_7"]}}     |
| Crimson Cascade T-Shirt | {object={"stock": {"S": 8, "M": 12, "L": 9, "XL": 3}, "locations": ["warehouse_4", "store_8"]}}    |
+-------------------------+----------------------------------------------------------------------------------------------------+
```

You can combine the `->` and `->>` operators to retrieve nested JSON properties. For example, this query retrieves the "S" size stock from the nested `inventory` object in the `properties` column:

```console
sql> select name, properties->'inventory'->'stock'->>'S' "available S size" from products;
+-------------------------+------------------+
|           name          | available S size |
|         varchar         |      varchar     |
+-------------------------+------------------+
| Ink Fusion T-Shirt      | 12               |
| ThreadVerse T-Shirt     | 7                |
| Design Dynamo T-Shirt   |                  |
| Artistry Apex T-Shirt   |                  |
| Graphite Glow T-Shirt   | 10               |
| Sunburst Shine T-Shirt  | 20               |
| Oceanic Opal T-Shirt    | 5                |
| Crimson Cascade T-Shirt | 8                |
+-------------------------+------------------+
```

Use an index to retrieve a specific element from a JSON array. For example, this query retrieves the first store with a product in stock:

```console
sql> select name, properties->'inventory'->'locations'->>0 "Store" from products;
+-------------------------+-------------+
|           name          |    Store    |
|         varchar         |   varchar   |
+-------------------------+-------------+
| Ink Fusion T-Shirt      | warehouse_1 |
| ThreadVerse T-Shirt     | warehouse_2 |
| Design Dynamo T-Shirt   | warehouse_3 |
| Artistry Apex T-Shirt   | warehouse_1 |
| Graphite Glow T-Shirt   | warehouse_2 |
| Sunburst Shine T-Shirt  | warehouse_1 |
| Oceanic Opal T-Shirt    | warehouse_3 |
| Crimson Cascade T-Shirt | warehouse_4 |
+-------------------------+-------------+
```

Retrieve the products with the colors black and white using the `->>` operator in the `WHERE` clause:

```console
sql> SELECT name, properties ->> 'color' color FROM products
WHERE properties ->> 'color' IN ('black', 'white');
+---------------------+---------+
|         name        |  color  |
|       varchar       | varchar |
+---------------------+---------+
| Ink Fusion T-Shirt  | white   |
| ThreadVerse T-Shirt | black   |
+---------------------+---------+
```

## Using views to simplify working with JSON columns

Views can be used to add extra columns representing JSON fields. For example:

```yaml
views:
  - name: products_with_color
    sql: |
      SELECT products.*, properties->>'color' color from products;
```

Query products and their colors using the created view:

```console
sql> describe products_with_color;
+-------------+-----------+-------------+
| column_name | data_type | is_nullable |
|   varchar   |  varchar  |   varchar   |
+-------------+-----------+-------------+
| id          | Int64     | YES         |
| name        | Utf8      | YES         |
| properties  | Utf8      | YES         |
| color       | Utf8      | YES         |
+-------------+-----------+-------------+
```

```console
sql> select id, name, color from products_with_color;
+-------+-------------------------+---------+
|   id  |           name          |  color  |
| int64 |         varchar         | varchar |
+-------+-------------------------+---------+
| 1     | Ink Fusion T-Shirt      | white   |
| 2     | ThreadVerse T-Shirt     | black   |
| 3     | Design Dynamo T-Shirt   | blue    |
| 4     | Artistry Apex T-Shirt   | red     |
| 5     | Graphite Glow T-Shirt   | gray    |
| 6     | Sunburst Shine T-Shirt  | yellow  |
| 7     | Oceanic Opal T-Shirt    | teal    |
| 8     | Crimson Cascade T-Shirt | maroon  |
+-------+-------------------------+---------+
```

## Further Reading

JSON strings manipulation with [datafusion-functions-json](https://github.com/datafusion-contrib/datafusion-functions-json).
