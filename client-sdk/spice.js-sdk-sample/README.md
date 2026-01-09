# Spice.js SDK Sample

A Node.js sample application demonstrating the [`@spiceai/spice`](https://www.npmjs.com/package/@spiceai/spice) package with the NYC taxi_trips dataset.

## Features

- **Dual Mode Support**: Works with both Spice.ai Cloud ☁️ and local Spice runtime 🏠
- Queries the NYC taxi_trips dataset using both `.sql()` and `.sqlJson()` methods
- Demonstrates four practical analytics queries:
  1. **Most Expensive Trips** - Find the top 10 highest-fare taxi rides
  2. **Trip Statistics** - Calculate average fares, distances, tips, and more
  3. **Popular Pickup Locations** - Identify the busiest pickup spots
  4. **Payment Type Distribution** - Analyze payment methods and tipping patterns

## Prerequisites

- Node.js 20 or higher
- npm or yarn

## Getting Started

1. Clone the Spice.ai cookbook repository:

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/client-sdk/spice.js-sdk-sample
```

2. Install dependencies:

```bash
npm install
```

## Usage

You can run this sample in two ways:

### Option 1: Using Local Spice Runtime 🏠 (Recommended)

1. Install the Spice CLI (see [Installation Guide](https://spiceai.org/docs/installation))
2. From the `cookbook/client-sdk/spice.js-sdk-sample` directory, start the Spice runtime:

```bash
# Terminal 1: Start Spice runtime (loads spicepod.yaml)
spice run
```

3. In a separate terminal, run the sample:

```bash
# Terminal 2: Run the sample (from the same directory)
node index.js
```

The sample will automatically connect to the local runtime at `localhost:50051`.

### Option 2: Using Spice.ai Cloud ☁️

1. Sign up for a free account at [spice.ai](https://spice.ai)
2. Create a new Spice app and manually deploy the `spicepod.yaml` through the web interface
   - For detailed instructions, see the [Getting Started Guide](https://docs.spice.ai/getting-started/get-started)
3. Get your API key from the Spice.ai dashboard
4. Create a `.env` file with your API key:

```env
# .env file
SPICE_API_KEY=your_api_key_here
```

5. Run the sample:

```bash
node index.js
```

The sample automatically detects which mode to use based on whether `SPICE_API_KEY` is set.

## Example Output

The application will display:

```shell
🌶️  Spice.js initialized
   Platform: Node.js v24.9.0 darwin arm64
   Transport: Arrow Flight → HTTP
   Endpoint: http://127.0.0.1:8090
   Flight URL: 127.0.0.1:50051
🚕 NYC Taxi Trips Data Analysis

📡 Connected to: Local Spice Runtime 🏠
💡 Tip: Set SPICE_API_KEY in .env to use Spice.ai Cloud

Querying taxi_trips dataset...

============================================================

📊 Query 1: Top 10 Most Expensive Taxi Trips

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

⏱️  Execution time: 27.59ms

============================================================

📈 Query 2: Trip Statistics Summary

Statistics from sample:
  • Total trips analyzed: 2964624
  • Average fare: $26.8
  • Average distance: 3.65 miles
  • Average tip: $3.34
  • Highest fare: $5000
  • Lowest fare: $-900

⏱️  Execution time: 9.25ms

============================================================

📍 Query 3: Top 10 Popular Pickup Locations

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

⏱️  Execution time: 9.00ms

============================================================

💳 Query 4: Payment Type Distribution

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

⏱️  Execution time: 17.14ms

============================================================

🔢 Query 5: Parametrized Query - Trips by Distance Range

Using .sql() with parameters for safe, dynamic queries

Trips with distance between 5 and 10 miles:

1. 5.99 miles - $313.74 total - $99.99 tip - 4 passenger(s)
2. 5.84 miles - $311.00 total - $15.00 tip - 1 passenger(s)
3. 7.47 miles - $307.75 total - $15.00 tip - 2 passenger(s)
4. 7.93 miles - $297.75 total - $0.00 tip - 1 passenger(s)
5. 7.18 miles - $282.75 total - $5.00 tip - 1 passenger(s)

⏱️  Execution time: 8.91ms

💡 Parameters used: $1=5, $2=10, $3=5

============================================================

📝 Method Comparison:

• .sql() - Uses Apache Arrow Flight (gRPC)
  ✓ Higher performance and efficiency
  ✓ Better for large datasets and high-throughput applications
  ✓ Returns Arrow Tables (columnar format)
  ✓ Supports parametrized queries ($1, $2, ... placeholders)
  ⚠️  Works in true Node.js runtimes (local Node.js, Lambda)

• .sqlJson() - Uses HTTP
  ✓ Simpler integration, works everywhere HTTP does
  ✓ Better for smaller queries and web applications
  ✓ Returns plain JavaScript objects (easier to work with)
  ✓ Works in browsers, Vercel, Netlify, and sandbox environments

============================================================

✅ Analysis complete!
```

## Code Examples

### Connecting to Spice

```javascript
const { SpiceClient } = require('@spiceai/spice');

// Option 1: Spice.ai Cloud (with API key)
const spiceCloud = new SpiceClient('your_api_key');

// Option 2: Local Spice Runtime (default: localhost:50051)
const spiceLocal = new SpiceClient();
```

### Querying Data

The SDK provides two query methods:

**`.sql()` - Apache Arrow Flight (gRPC)**

- Higher performance and efficiency
- Better for large datasets and high-throughput applications
- Returns Apache Arrow Tables (columnar format)
- Works in Node.js, AWS Lambda, and other server environments

```javascript
const result = await spice.sql('SELECT * FROM taxi_trips LIMIT 10');
const data = result.toArray();
```

**`.sqlJson()` - HTTP/REST**

- Simpler integration, works everywhere HTTP does
- Better for smaller queries and web applications
- Returns plain JavaScript objects
- Works in browsers, Vercel, Netlify, and edge functions

```javascript
const result = await spice.sqlJson('SELECT * FROM taxi_trips LIMIT 10');
const data = result.data;
```

## About the Dataset

This sample uses the NYC taxi_trips dataset, which contains real taxi trip data including fares, distances, pickup/dropoff times, and locations.

- **Local**: The dataset is defined in `spicepod.yaml` and will be loaded automatically when you run `spice run`
- **Cloud**: Manually deploy `spicepod.yaml` to Spice Cloud through the web interface. See the [Getting Started Guide](https://docs.spice.ai/getting-started/get-started) for help.
