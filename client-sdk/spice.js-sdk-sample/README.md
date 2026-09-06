# Spice.js SDK Sample

Works with `v1.0+`

Use [`@spiceai/spice`](https://www.npmjs.com/package/@spiceai/spice) from Node.js to query `taxi_trips`.

## What This Sample Includes

- `index.js`: Main sample with multiple analytics queries.
- `index_cloud.mjs`: Minimal cloud-only query (`show tables;`).

## Prerequisites

- Node.js 20+
- npm
- [Spice CLI](https://docs.spiceai.org/getting-started) for local mode

## Quick Start

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/client-sdk/spice.js-sdk-sample
npm install
```

## Run with Local Spice Runtime

Start Spice runtime in one terminal:

```bash
spice run
```

Run the Node sample in another terminal:

```bash
npm start
```

`index.js` runs against your local runtime by default.

## Run with Spice.ai Cloud

Set your API key for the commands in this README:

```bash
export SPICE_API_KEY="your_api_key"
```

`index.js` reads `SPICE_API_KEY` (from the environment or a `.env` file) and connects to
Spice.ai Cloud instead of the local runtime when it is set - no code edit needed:

```bash
npm start
```

`index_cloud.mjs` is a minimal cloud-only snippet and keeps an inline API key placeholder
by design. Replace the API key placeholder in `index_cloud.mjs` with `${SPICE_API_KEY}`,
then run:

```bash
node index_cloud.mjs
```

## Example Output

The application prints output similar to:

```text
Spice.js initialized
  Platform: Node.js v24.9.0 darwin arm64
  Transport: Arrow Flight -> HTTP
  Endpoint: http://127.0.0.1:8090
  Flight URL: 127.0.0.1:50051
NYC Taxi Trips Data Analysis

Connected to: Local Spice Runtime
Tip: Set SPICE_API_KEY in .env to use Spice.ai Cloud

Querying taxi_trips dataset...

============================================================

Query 1: Top 10 Most Expensive Taxi Trips

Using .sql() - Apache Arrow Flight (gRPC) for high performance

Found 10 trips:

1. $5000.00 - 0 miles - 0 passenger(s)
2. $5000.00 - 0 miles - 0 passenger(s)
3. $2500.00 - 0 miles - 0 passenger(s)
4. $2500.00 - 0 miles - 0 passenger(s)
5. $2500.00 - 0 miles - 0 passenger(s)
6. $2225.30 - 31.95 miles - 1 passenger(s)
7. $1617.50 - 233.25 miles - 1 passenger(s)
8. $1000.00 - 0 miles - 0 passenger(s)
9. $940.93 - 142.62 miles - 1 passenger(s)
10. $900.00 - 157.25 miles - 1 passenger(s)

Execution time: 27.59ms

============================================================

Query 2: Trip Statistics Summary

Statistics from sample:
  - Total trips analyzed: 2964624
  - Average fare: $26.8
  - Average distance: 3.65 miles
  - Average tip: $3.34
  - Highest fare: $5000
  - Lowest fare: $-900

Execution time: 9.25ms

============================================================

Query 3: Top 10 Popular Pickup Locations

Most popular pickup locations:

1. Location ID 132:
  145240 trips | Avg fare: $76.58 | Avg distance: 15.49 miles
2. Location ID 161:
  143471 trips | Avg fare: $23.48 | Avg distance: 2.56 miles
3. Location ID 237:
  142708 trips | Avg fare: $19.45 | Avg distance: 1.7 miles
4. Location ID 236:
  136465 trips | Avg fare: $20 | Avg distance: 1.85 miles
5. Location ID 162:
  106717 trips | Avg fare: $22.88 | Avg distance: 2.23 miles
6. Location ID 230:
  106324 trips | Avg fare: $26.27 | Avg distance: 2.91 miles
7. Location ID 186:
  104523 trips | Avg fare: $23.64 | Avg distance: 2.27 miles
8. Location ID 142:
  104080 trips | Avg fare: $21 | Avg distance: 2.09 miles
9. Location ID 138:
  89533 trips | Avg fare: $65.01 | Avg distance: 9.59 miles
10. Location ID 239:
  88474 trips | Avg fare: $20.93 | Avg distance: 2.26 miles

Execution time: 9.00ms

============================================================

Query 4: Payment Type Distribution

Using .sqlJson() - HTTP transport for simpler integration

Payment type breakdown:

1. Credit card (Type 1):
  2,319,046 trips | Avg amount: $28.26 | Avg tip: $4.17
2. Cash (Type 2):
  439,191 trips | Avg amount: $22.88 | Avg tip: $0
3. Dispute (Type 4):
  46,628 trips | Avg amount: $1.77 | Avg tip: $0.04
4. No charge (Type 3):
  19,597 trips | Avg amount: $8.76 | Avg tip: $0.01

Execution time: 17.14ms

============================================================

Query 5: Parametrized Query - Trips by Distance Range

Using .sql() with parameters for safe, dynamic queries

Trips with distance between 5 and 10 miles:

1. 5.99 miles - $313.74 total - $99.99 tip - 4 passenger(s)
2. 5.84 miles - $311.00 total - $15.00 tip - 1 passenger(s)
3. 7.47 miles - $307.75 total - $15.00 tip - 2 passenger(s)
4. 7.93 miles - $297.75 total - $0.00 tip - 1 passenger(s)
5. 7.18 miles - $282.75 total - $5.00 tip - 1 passenger(s)

Execution time: 8.91ms

Parameters used: $1=5, $2=10, $3=5

============================================================

Method Comparison:

.sql() - Uses Apache Arrow Flight (gRPC)
  - Higher performance and efficiency
  - Better for large datasets and high-throughput applications
  - Returns Arrow Tables (columnar format)
  - Supports parametrized queries ($1, $2, ... placeholders)
  - Works in true Node.js runtimes (local Node.js, Lambda)

.sqlJson() - Uses HTTP
  - Simpler integration, works everywhere HTTP does
  - Better for smaller queries and web applications
  - Returns plain JavaScript objects (easier to work with)
  - Works in browsers, Vercel, Netlify, and sandbox environments

============================================================

Analysis complete!
```

## Optional: Minimal Cloud-Only Script

```bash
node index_cloud.mjs
```

Expected output is a table list from `show tables;`.

## Advanced and More

### Features

- Dual mode support: local Spice runtime and Spice.ai Cloud.
- Uses both `.sql()` and `.sqlJson()` query methods.
- Includes five analytics query examples over `taxi_trips`.

### Detailed Cloud Setup

1. Create a free account at [spice.ai](https://spice.ai).
2. Create a Spice.ai Cloud app.
3. Deploy this sample's `spicepod.yaml` to your Cloud app.
4. Set `SPICE_API_KEY`, then replace the API key placeholder in `index_cloud.mjs` with that value.
5. Run `node index_cloud.mjs`.

### Code Examples

Connect to Spice:

```javascript
const { SpiceClient } = require("@spiceai/spice");

// Cloud
const spiceCloud = new SpiceClient({ apiKey: process.env.SPICE_API_KEY });

// Local (default localhost runtime)
const spiceLocal = new SpiceClient();
```

Query with `.sql()` (Arrow Flight / gRPC):

```javascript
const result = await spice.sql("SELECT * FROM taxi_trips LIMIT 10");
const rows = result.toArray();
```

Query with `.sqlJson()` (HTTP):

```javascript
const result = await spice.sqlJson("SELECT * FROM taxi_trips LIMIT 10");
const rows = result.data;
```

### About the Dataset

This sample uses the NYC `taxi_trips` dataset.

- Local mode: dataset is defined in `spicepod.yaml` and loads with `spice run`.
- Cloud mode: deploy `spicepod.yaml` to your Cloud app before running queries.

## Links

- [spice.js SDK](https://github.com/spiceai/spice.js)
- [npm package](https://www.npmjs.com/package/@spiceai/spice)
- [Spice.ai Cloud](https://spice.ai)
- [Spice.ai documentation](https://docs.spiceai.org)
