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
npm start
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
npm start
```

The sample automatically detects which mode to use based on whether `SPICE_API_KEY` is set.

## Example Output

The application will display:

```shell
🚕 NYC Taxi Trips Data Analysis

Querying taxi_trips dataset using Spice.ai...

============================================================

📊 Query 1: Top 10 Most Expensive Taxi Trips

Using .sql() - Apache Arrow Flight (gRPC) for high performance

Found 10 trips:

1. $450.30 - 18.5 miles - 2 passenger(s)
2. $401.30 - 0.0 miles - 1 passenger(s)
3. $400.00 - 1.72 miles - 1 passenger(s)
...

⏱️  Execution time: 245.12ms

============================================================

📈 Query 2: Trip Statistics Summary

Statistics from sample:
  • Total trips analyzed: 1000
  • Average fare: $19.55
  • Average distance: 3.45 miles
  • Average tip: $2.89
  • Highest fare: $450.30
  • Lowest fare: $3.50

⏱️  Execution time: 189.45ms

============================================================

📍 Query 3: Top 10 Popular Pickup Locations

Most popular pickup locations:

1. Location ID 237:
   12,345 trips | Avg fare: $18.20 | Avg distance: 2.8 miles
...

⏱️  Execution time: 312.78ms

============================================================

💳 Query 4: Payment Type Distribution

Using .sqlJson() - HTTP transport for simpler integration

Payment type breakdown:

1. Credit card (Type 1):
   45,678 trips | Avg amount: $21.30 | Avg tip: $3.50
2. Cash (Type 2):
   23,456 trips | Avg amount: $18.90 | Avg tip: $0.10
...

⏱️  Execution time: 156.23ms

============================================================

📝 Method Comparison:

• .sql() - Uses Apache Arrow Flight (gRPC)
  ✓ Higher performance and efficiency
  ✓ Better for large datasets and high-throughput applications
  ✓ Returns Arrow Tables (columnar format)
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
