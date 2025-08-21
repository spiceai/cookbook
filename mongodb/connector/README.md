# MongoDB Data Connector

This recipe will use a demo instance of MongoDB with a generated dataset. Follow the recipe to create MongoDB instance and get started with MongoDB as a Data Connector.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)is installed
- Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation).

## Steps

**Step 1.** Optional. Start a MongoDB instance using Docker

```bash
docker run --name mongodb-cookbook -e MONGO_INITDB_ROOT_USERNAME=root -e MONGO_INITDB_ROOT_PASSWORD=password -e MONGO_INITDB_DATABASE=mongo_db -p 27018:27017 -d mongo:7.0
```

**Step 2.** Create a sample MongoDB database and generate a testing collection

Invoke MongoDB in the prompt.

```bash
docker exec -i mongodb-cookbook mongosh -u root -p password --authenticationDatabase admin <<'EOF'
use spice_demo;
db.sample_data.drop();

const BASE_MS  = new Date("2024-01-01T01:00:00Z").getTime();
const YEAR_MS  = 365 * 24 * 60 * 60 * 1000;
const pad = (n, w) => n.toString().padStart(w, "0");
const round6 = n => Math.round(n * 1e6) / 1e6;

const BATCH = 1000;
let ops = [];

for (let i = 0; i < 20000; i++) {
  const doc = {
    datetime: new Date(BASE_MS + Math.floor(Math.random() * YEAR_MS)),
    name: `Name${Math.floor(Math.random() * 100)}`,
    phone: `555-${pad(Math.floor(Math.random() * 10000), 4)}`,
    email: `user${Math.floor(Math.random() * 100)}@example.com`,
    street_address: `Street${Math.floor(Math.random() * 100)} Avenue`,
    zip_code: pad(Math.floor(Math.random() * 100000), 5),
    region: `Region${Math.floor(Math.random() * 10)}`,
    location: {lat:  round6(-90  + 180 * Math.random()), lon: round6(-180 + 360 * Math.random())},
  };

  ops.push({ insertOne: { document: doc } });
  if (ops.length === BATCH) { db.sample_data.bulkWrite(ops); ops = []; }
}
if (ops.length) db.sample_data.bulkWrite(ops);

db.sample_data.createIndex({ datetime: 1 });
db.sample_data.createIndex({ region: 1 });
db.sample_data.countDocuments();
EOF
```

Check the sample data generated in the `sample_data` collection.

```bash
docker exec -i mongodb-cookbook mongosh -u root -p password --authenticationDatabase admin --quiet --eval 'printjson(db.getSiblingDB("spice_demo").sample_data.findOne())'
```

```bash
{
  _id: ObjectId('689f6f87d79dc5f23b74e39a'),
  datetime: ISODate('2024-08-24T11:43:09.535Z'),
  name: 'Name55',
  phone: '555-7719',
  email: 'user80@example.com',
  street_address: 'Street97 Avenue',
  zip_code: '50487',
  region: 'Region6',
  location: {
    lat: -7.499683,
    lon: 178.565729
  }
}
```

**Step 3.** Initialize a Spice app.

```bash
spice init mongodb-demo
cd mongodb-demo
```

**Step 4.** Configure the dataset to connect to MongoDB. Copy and paste the configuration below to `spicepod.yaml` in the Spice app.

```yaml
version: v1
kind: Spicepod
name: mongodb-demo
datasets:
  - from: mongodb:sample_data
    name: sample_data
    params:
      mongodb_host: localhost
      mongodb_port: 27018
      mongodb_db: spice_demo
      mongodb_sslmode: disabled
      mongodb_user: root
      mongodb_auth_source: admin
      mongodb_unnest_depth: 1
      mongodb_pass: ${env:MONGODB_PASS}
```

Ensure the `MONGODB_PASS` environment variable is set to the password for your MongoDB instance. Environment variables can be specified on the command line when running the Spice runtime or in a `.env` file in the same directory as `spicepod.yaml`.

```bash
echo "MONGODB_PASS=<password>" > .env
# i.e. echo "MONGODB_PASS=123" > .env
```

**Step 5.** Start the Spice runtime

```bash
spice run
```

Confirm in the terminal output the `sample_data` dataset has been loaded:

```bash
2025/01/13 11:52:51 INFO Spice.ai runtime starting...
2025-01-13T19:52:51.473621Z  INFO runtime::init::dataset: Initializing dataset sample_data
2025-01-13T19:52:51.474059Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2025-01-13T19:52:51.474795Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-01-13T19:52:51.474869Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-01-13T19:52:51.481201Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2025-01-13T19:52:51.491591Z  INFO runtime::init::dataset: Dataset sample_data registered (mongodb:sample_data).
2025-01-13T19:52:51.673260Z  INFO runtime::init::results_cache: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
```

Follow the [getting started guide](https://docs.spiceai.org/getting-started) to get started with the Spice.ai runtime.

See the [datasets reference](https://docs.spiceai.org/reference/spicepod/datasets) for more dataset configuration options.

**Step 6.** Run queries against the dataset using the Spice SQL REPL.

In a new terminal, start the Spice SQL REPL

```bash
spice sql
```

You can now now query `sample_data` in the runtime.

```sql
select * from sample_data limit 10;
```

```console
+--------+----------+---------+--------------------------+-----------------+----------+--------------+--------------+--------------------------+--------------------+
| name   | phone    | region  | _id                      | street_address  | zip_code | location.lat | location.lon | datetime                 | email              |
+--------+----------+---------+--------------------------+-----------------+----------+--------------+--------------+--------------------------+--------------------+
| Name55 | 555-7719 | Region6 | 689f6f87d79dc5f23b74e39a | Street97 Avenue | 50487    | -7.499683    | 178.565729   | 2024-08-24T11:43:09.535Z | user80@example.com |
| Name19 | 555-3343 | Region9 | 689f6f87d79dc5f23b74e39b | Street55 Avenue | 83057    | 57.780531    | -75.688056   | 2024-03-26T07:35:18.845Z | user15@example.com |
| Name51 | 555-8686 | Region8 | 689f6f87d79dc5f23b74e39c | Street28 Avenue | 14969    | -41.685444   | -90.492728   | 2024-11-14T04:00:01.456Z | user19@example.com |
| Name49 | 555-2445 | Region4 | 689f6f87d79dc5f23b74e39d | Street94 Avenue | 14028    | 29.514682    | 141.89367    | 2024-07-28T13:25:10.319Z | user81@example.com |
| Name97 | 555-8467 | Region7 | 689f6f87d79dc5f23b74e39e | Street15 Avenue | 55554    | -83.690002   | -175.602263  | 2024-02-26T05:21:43.347Z | user39@example.com |
| Name82 | 555-1579 | Region3 | 689f6f87d79dc5f23b74e39f | Street8 Avenue  | 29491    | 13.70095     | -165.815156  | 2024-03-21T17:21:57.770Z | user30@example.com |
| Name40 | 555-9487 | Region8 | 689f6f87d79dc5f23b74e3a0 | Street0 Avenue  | 58227    | -23.839752   | 18.036466    | 2024-09-09T06:54:50.403Z | user51@example.com |
| Name92 | 555-5474 | Region1 | 689f6f87d79dc5f23b74e3a1 | Street47 Avenue | 54678    | -35.417564   | -120.375898  | 2024-01-24T10:33:31.687Z | user91@example.com |
| Name4  | 555-8745 | Region8 | 689f6f87d79dc5f23b74e3a2 | Street61 Avenue | 67033    | -85.346894   | -112.861349  | 2024-05-24T14:07:49.690Z | user65@example.com |
| Name22 | 555-5701 | Region8 | 689f6f87d79dc5f23b74e3a3 | Street40 Avenue | 18669    | -14.759925   | 162.383958   | 2024-10-29T11:51:28.992Z | user47@example.com |
+--------+----------+---------+--------------------------+-----------------+----------+--------------+--------------+--------------------------+--------------------+

Time: 0.011687958 seconds. 10 rows.
```

For more information on using `spice sql`, see the [CLI reference](https://docs.spiceai.org/cli/reference/sql).

**Step 6.** Cleanup

```bash
docker rm -f mongodb-cookbook 
```