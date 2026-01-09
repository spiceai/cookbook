const { SpiceClient } = require("@spiceai/spice");
require("dotenv").config();

const API_KEY = process.env.SPICE_API_KEY;

async function main() {
  // Determine which client to use
  const usingCloud = !!API_KEY;

  // Initialize Spice client
  //
  const client = usingCloud
    ? // Option 1: Connect to Spice.ai Cloud (requires API key)
      // Get your free API key at https://spice.ai
      new SpiceClient({
        apiKey: API_KEY,
      })
    : // Option 2: Connect to local Spice runtime (default: localhost:50051)
      // Start local runtime with: spice run
      new SpiceClient();

  console.log("🚕 NYC Taxi Trips Data Analysis\n");
  console.log(
    `📡 Connected to: ${
      usingCloud ? "Spice.ai Cloud ☁️" : "Local Spice Runtime 🏠"
    }`,
  );
  if (!usingCloud) {
    console.log("💡 Tip: Set SPICE_API_KEY in .env to use Spice.ai Cloud\n");
  } else {
    console.log("");
  }

  try {
    console.log("Querying taxi_trips dataset...\n");
    console.log("=".repeat(60));

    // Query 1: Get top 10 most expensive taxi trips
    console.log("\n📊 Query 1: Top 10 Most Expensive Taxi Trips\n");
    console.log(
      "Using .sql() - Apache Arrow Flight (gRPC) for high performance\n",
    );
    const expensiveTripsQuery = `
      SELECT
        total_amount,
        trip_distance,
        tpep_pickup_datetime,
        tpep_dropoff_datetime,
        passenger_count,
        PULocationID,
        DOLocationID
      FROM taxi_trips
      ORDER BY total_amount DESC
      LIMIT 10
    `;

    const start1 = performance.now();
    const expensiveTrips = await client.sql(expensiveTripsQuery);
    const expensiveTripsArray = expensiveTrips.toArray();
    const end1 = performance.now();

    console.log(`Found ${expensiveTripsArray.length} trips:\n`);
    expensiveTripsArray.forEach((trip, idx) => {
      console.log(
        `${idx + 1}. $${trip.total_amount.toFixed(2)} - ${
          trip.trip_distance
        } miles - ${trip.passenger_count} passenger(s)`,
      );
    });

    console.log(`\n⏱️  Execution time: ${(end1 - start1).toFixed(2)}ms`);

    // Query 2: Average fare and trip statistics
    console.log("\n" + "=".repeat(60));
    console.log("\n📈 Query 2: Trip Statistics Summary\n");
    const statsQuery = `
      SELECT
        COUNT(*) as total_trips,
        ROUND(AVG(total_amount), 2) as avg_fare,
        ROUND(AVG(trip_distance), 2) as avg_distance,
        ROUND(AVG(tip_amount), 2) as avg_tip,
        MAX(total_amount) as max_fare,
        MIN(total_amount) as min_fare
      FROM taxi_trips
      LIMIT 1000
    `;

    const start2 = performance.now();
    const stats = await client.sql(statsQuery);
    const statsArray = stats.toArray();
    const end2 = performance.now();
    const tripStats = statsArray[0];

    console.log("Statistics from sample:");
    console.log(`  • Total trips analyzed: ${tripStats.total_trips}`);
    console.log(`  • Average fare: $${tripStats.avg_fare}`);
    console.log(`  • Average distance: ${tripStats.avg_distance} miles`);
    console.log(`  • Average tip: $${tripStats.avg_tip}`);
    console.log(`  • Highest fare: $${tripStats.max_fare}`);
    console.log(`  • Lowest fare: $${tripStats.min_fare}`);

    console.log(`\n⏱️  Execution time: ${(end2 - start2).toFixed(2)}ms`);

    // Query 3: Popular pickup locations
    console.log("\n" + "=".repeat(60));
    console.log("\n📍 Query 3: Top 10 Popular Pickup Locations\n");
    const locationsQuery = `
      SELECT
        PULocationID,
        COUNT(*) as trip_count,
        ROUND(AVG(total_amount), 2) as avg_fare,
        ROUND(AVG(trip_distance), 2) as avg_distance
      FROM taxi_trips
      GROUP BY PULocationID
      ORDER BY trip_count DESC
      LIMIT 10
    `;

    const start3 = performance.now();
    const locations = await client.sql(locationsQuery);
    const locationsArray = locations.toArray();
    const end3 = performance.now();

    console.log("Most popular pickup locations:\n");
    locationsArray.forEach((loc, idx) => {
      console.log(`${idx + 1}. Location ID ${loc.PULocationID}:`);
      console.log(
        `   ${loc.trip_count} trips | Avg fare: $${loc.avg_fare} | Avg distance: ${loc.avg_distance} miles`,
      );
    });

    console.log(`\n⏱️  Execution time: ${(end3 - start3).toFixed(2)}ms`);

    // Query 4: Payment type distribution using .sqlJson()
    console.log("\n" + "=".repeat(60));
    console.log("\n💳 Query 4: Payment Type Distribution\n");
    console.log("Using .sqlJson() - HTTP transport for simpler integration\n");
    const paymentQuery = `
      SELECT
        payment_type,
        COUNT(*) as count,
        ROUND(AVG(total_amount), 2) as avg_amount,
        ROUND(AVG(tip_amount), 2) as avg_tip
      FROM taxi_trips
      WHERE payment_type IN (1, 2, 3, 4)
      GROUP BY payment_type
      ORDER BY count DESC
    `;

    // Use .sqlJson() which returns plain JSON over HTTP
    const start4 = performance.now();
    const paymentResult = await client.sqlJson(paymentQuery);
    const end4 = performance.now();
    const paymentData = paymentResult.data;

    console.log("Payment type breakdown:\n");

    const paymentTypes = {
      1: "Credit card",
      2: "Cash",
      3: "No charge",
      4: "Dispute",
    };

    paymentData.forEach((payment, idx) => {
      const typeName = paymentTypes[payment.payment_type] || "Unknown";
      console.log(`${idx + 1}. ${typeName} (Type ${payment.payment_type}):`);
      console.log(
        `   ${payment.count.toLocaleString()} trips | Avg amount: $${
          payment.avg_amount
        } | Avg tip: $${payment.avg_tip}`,
      );
    });

    console.log(`\n⏱️  Execution time: ${(end4 - start4).toFixed(2)}ms`);

    // Query 5: Parametrized query example
    console.log("\n" + "=".repeat(60));
    console.log("\n🔢 Query 5: Parametrized Query - Trips by Distance Range\n");
    console.log("Using .sql() with parameters for safe, dynamic queries\n");

    const minDistance = 5;
    const maxDistance = 10;
    const limitRows = 5;

    const parametrizedQuery = `
      SELECT
        trip_distance,
        total_amount,
        tip_amount,
        passenger_count,
        tpep_pickup_datetime
      FROM taxi_trips
      WHERE trip_distance >= $1 AND trip_distance <= $2
      ORDER BY total_amount DESC
      LIMIT $3
    `;

    const start5 = performance.now();
    const parametrizedResult = await client.sql(parametrizedQuery, {
      parameters: [minDistance, maxDistance, limitRows],
    });
    const parametrizedArray = parametrizedResult.toArray();
    const end5 = performance.now();

    console.log(
      `Trips with distance between ${minDistance} and ${maxDistance} miles:\n`,
    );
    parametrizedArray.forEach((trip, idx) => {
      console.log(
        `${idx + 1}. ${trip.trip_distance} miles - $${trip.total_amount.toFixed(
          2,
        )} total - $${trip.tip_amount.toFixed(2)} tip - ${
          trip.passenger_count
        } passenger(s)`,
      );
    });

    console.log(`\n⏱️  Execution time: ${(end5 - start5).toFixed(2)}ms`);
    console.log(
      "\n💡 Parameters used: $1=" +
        minDistance +
        ", $2=" +
        maxDistance +
        ", $3=" +
        limitRows,
    );

    console.log("\n" + "=".repeat(60));
    console.log("\n📝 Method Comparison:\n");
    console.log("• .sql() - Uses Apache Arrow Flight (gRPC)");
    console.log("  ✓ Higher performance and efficiency");
    console.log(
      "  ✓ Better for large datasets and high-throughput applications",
    );
    console.log("  ✓ Returns Arrow Tables (columnar format)");
    console.log("  ✓ Supports parametrized queries ($1, $2, ... placeholders)");
    console.log(
      "  ⚠️  Works in true Node.js runtimes (local Node.js, Lambda)\n",
    );
    console.log("• .sqlJson() - Uses HTTP");
    console.log("  ✓ Simpler integration, works everywhere HTTP does");
    console.log("  ✓ Better for smaller queries and web applications");
    console.log("  ✓ Returns plain JavaScript objects (easier to work with)");
    console.log(
      "  ✓ Works in browsers, Vercel, Netlify, and sandbox environments",
    );

    console.log("\n" + "=".repeat(60));
    console.log("\n✅ Analysis complete!");
  } catch (error) {
    console.error("❌ Error occurred:", error.message);
    console.error("Stack trace:", error.stack);
    process.exit(1);
  }
}

// Run the main function
main();
