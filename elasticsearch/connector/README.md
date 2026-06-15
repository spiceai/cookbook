# Elasticsearch Data Connector

Works with `v2.0+`

This recipe demonstrates how to query Elasticsearch indices from Spice using federated SQL. It includes:

- `articles` — a federated dataset queried directly from Elasticsearch
- `all_types` — a federated dataset covering supported Elasticsearch field types

The Elasticsearch connector can also power `vector_search`, `text_search`, and `rrf` for indices that contain the required search fields.

## Prerequisites

- **Spice with Elasticsearch support**: the Elasticsearch connector is not included in the released binaries. Build and run Spice with the `elasticsearch` feature enabled, e.g. `cargo run --release --features elasticsearch -p spiced`. See the [Elasticsearch Data Connector documentation](https://spiceai.org/docs/components/data-connectors/elasticsearch) for details.
- Docker installed

## Getting Started

### Step 1: Prepare the recipe directory

Change into the recipe directory:

```bash
cd cookbook/elasticsearch/connector
```

### Step 2: Start Elasticsearch and seed the sample indices

Start the local Elasticsearch service and seed the sample data:

```bash
docker compose up
```

Keep this running while you use the recipe.

### Step 3: Start the Spice runtime

In a new terminal, start the Spice runtime:

```bash
spice run
```

### Step 4: Open the Spice SQL REPL

In another terminal, open the Spice SQL REPL:

```bash
spice sql
```

### Step 5: Run a few example queries

Run a few basic federated SQL queries to verify the Elasticsearch datasets are available.

Query the `articles` index:

```sql
SELECT id, title, category, author
FROM articles
WHERE category = 'machine_learning'
LIMIT 10;
```

```
+----+----------------------------------------------------------------------------------+------------------+------------------+
| id |                                       title                                      |     category     |      author      |
|int32|                                      varchar                                     |      varchar     |      varchar     |
+----+----------------------------------------------------------------------------------+------------------+------------------+
| 6  | Cost-Aware AutoML on Kubernetes                                                  | machine_learning | Bob Martinez     |
| 14 | Contrastive Learning Explained: From Theory to Production                        | machine_learning | Priya Sharma     |
| 27 | How Federated Learning Is Transforming AI Applications                           | machine_learning | Quinn Walker     |
| 32 | Scaling Few-Shot Learning to Billions of Parameters                              | machine_learning | Tom Brennan      |
| 38 | Why understanding Generative Adversarial Networks Through Mathematical Intuition | machine_learning | Alice Chen       |
| 40 | Few-Shot Learning: State of the Art in 2025                                      | machine_learning | Luca Ferrari     |
| 45 | Attention Mechanisms: State of the Art in 2025                                   | machine_learning | Carol Okonkwo    |
| 47 | Why understanding Fine-Tuning Through Mathematical Intuition                     | machine_learning | Ravi Subramaniam |
| 63 | Scaling Self-Supervised Learning to Billions of Parameters                       | machine_learning | Priya Sharma     |
| 68 | A Practical Guide to Diffusion Models                                            | machine_learning | Luca Ferrari     |
+----+----------------------------------------------------------------------------------+------------------+------------------+

Time: 0.036074709 seconds. 10 rows.
```

Filter the `all_types` index on a keyword field:

```sql
SELECT *
FROM all_types
WHERE field_keyword = 'category_0';
```

```
+--------------------------+---------------+------------+-----------------------------------------------+----------------------+--------------------------------+-------------------------------------------------------------+--------------------------------------------+--------------------+--------------------------+-------------------------------------------------------+-------------+-------------------------+--------------------------------------+--------------------------------------------------------+------------------+---------------+-----------------------+---------------+---------------+---------------+---------------------------+---------------------------------------------------------------+-------------------+--------------------+--------------------+----------------------------------------+-------------+-----------------------------------------------------------+-------------------------------------+---------------------+---------------+----+
|       field_binary       | field_boolean | field_byte |                field_completion               |      field_date      |        field_date_nanos        |                       field_date_range                      |             field_dense_vector             |    field_double    |    field_double_range    |                    field_flattened                    | field_float |    field_float_range    |            field_geo_point           |                     field_geo_shape                    | field_half_float | field_integer |  field_integer_range  |    field_ip   | field_keyword |   field_long  |      field_long_range     |                          field_nested                         | field_object.name | field_object.value | field_scaled_float |        field_search_as_you_type        | field_short |                         field_text                        |          field_token_count          | field_unsigned_long | field_version | id |
|          varchar         |    boolean    |    int8    |                    varchar                    |        varchar       |             varchar            |                           varchar                           |                 float32[4]                 |       float64      |          varchar         |                        varchar                        |   float32   |         varchar         |                varchar               |                         varchar                        |      float32     |     int32     |        varchar        |    varchar    |    varchar    |     int64     |          varchar          |                            varchar                            |      varchar      |        int32       |       float32      |                 varchar                |    int16    |                          varchar                          |               varchar               |       varchar       |    varchar    |int32|
+--------------------------+---------------+------------+-----------------------------------------------+----------------------+--------------------------------+-------------------------------------------------------------+--------------------------------------------+--------------------+--------------------------+-------------------------------------------------------+-------------+-------------------------+--------------------------------------+--------------------------------------------------------+------------------+---------------+-----------------------+---------------+---------------+---------------+---------------------------+---------------------------------------------------------------+-------------------+--------------------+--------------------+----------------------------------------+-------------+-----------------------------------------------------------+-------------------------------------+---------------------+---------------+----+
| YmluYXJ5X3BheWxvYWRfNQ== | true          | -114       | {"input":["suggest_5","doc_5"],"weight":6}    | 2024-06-06T05:00:00Z | 2024-06-06T05:00:00.000000000Z | {"gte":"2024-01-06T00:00:00Z","lte":"2024-12-06T23:59:59Z"} | [-0.958924, -0.279415, 0.656987, 0.989358] | 680696.2410453358  | {"gte":5.5,"lte":5.51}   | {"arbitrary_key":"value_5","nested_key":{"deep":5}}   | 551.9171    | {"gte":5.0,"lte":5.5}   | {"lat":-21.463575,"lon":-143.289215} | {"type":"Point","coordinates":[-90.240943,41.613069]}  | -50.19           | 94455         | {"gte":50,"lte":55}   | 192.168.5.35  | category_0    | 24150178885   | {"gte":5000,"lte":5100}   | [{"tag":"tag_1","score":0.372},{"tag":"tag_2","score":0.868}] | obj_5             | 35                 | 51.85              | searchable text for document number 5  | 14225       | The quick brown fox jumps over the lazy dog — document 5  | token count source text document 5  | 261035185072990349  | 1.5.0         | 5  |
| YmluYXJ5X3BheWxvYWRfMTA= | false         | -121       | {"input":["suggest_10","doc_10"],"weight":11} | 2024-02-11T10:00:00Z | 2024-02-11T10:00:00.000000000Z | {"gte":"2024-01-11T00:00:00Z","lte":"2024-12-11T23:59:59Z"} | [-0.544021, -0.99999, -0.536573, 0.420167] | -587803.5357209966 | {"gte":11.0,"lte":11.01} | {"arbitrary_key":"value_10","nested_key":{"deep":10}} | 626.6425    | {"gte":10.0,"lte":10.5} | {"lat":-45.000598,"lon":163.014087}  | {"type":"Point","coordinates":[178.760517,-81.979851]} | 64.72            | 12430         | {"gte":100,"lte":105} | 192.168.10.70 | category_0    | -955323551533 | {"gte":10000,"lte":10100} | [{"tag":"tag_1","score":0.521},{"tag":"tag_2","score":0.328}] | obj_10            | 70                 | 653.47             | searchable text for document number 10 | 30482       | The quick brown fox jumps over the lazy dog — document 10 | token count source text document 10 | 79329244941176303   | 1.10.0        | 10 |
+--------------------------+---------------+------------+-----------------------------------------------+----------------------+--------------------------------+-------------------------------------------------------------+--------------------------------------------+--------------------+--------------------------+-------------------------------------------------------+-------------+-------------------------+--------------------------------------+--------------------------------------------------------+------------------+---------------+-----------------------+---------------+---------------+---------------+---------------------------+---------------------------------------------------------------+-------------------+--------------------+--------------------+----------------------------------------+-------------+-----------------------------------------------------------+-------------------------------------+---------------------+---------------+----+

Time: 0.024743022 seconds. 2 rows.
```

## Learn more

- [Elasticsearch Data Connector Documentation](https://spiceai.org/docs/components/data-connectors/elasticsearch)
- [Search Functionality Documentation](https://spiceai.org/docs/features/search)
- [Datasets Reference](https://docs.spiceai.org/reference/spicepod/datasets)
- [Spice SQL CLI Reference](https://docs.spiceai.org/cli/reference/sql)
