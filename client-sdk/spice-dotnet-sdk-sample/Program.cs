#pragma warning disable CS8321 // Local function is declared but never used

using Spice;
using Apache.Arrow;
using System.Globalization;

// Top-level statements
var client = new SpiceClientBuilder().Build();

Console.WriteLine("=== Using Query ===");
await Query(client);

Console.WriteLine("\n=== Using Query with Parameters ===");
await QueryWithParams(client, 5);

async Task Query(SpiceClient client)
{
    var result = await client.Query(
        "SELECT \"VendorID\", \"tpep_pickup_datetime\", \"fare_amount\" FROM taxi_trips LIMIT 10");

    await foreach (var batch in result)
    {
        PrintBatch(batch);
    }
}

async Task QueryWithParams(SpiceClient client, int limit)
{
    // Use positional parameters ($1, $2, etc.) with QueryWithParams
    var result = await client.QueryWithParams(
        "SELECT \"VendorID\", \"tpep_pickup_datetime\", \"fare_amount\" FROM taxi_trips LIMIT $1",
        limit);

    if (result == null)
    {
        Console.WriteLine("No results returned");
        return;
    }

    while (await result.ReadNextRecordBatchAsync() is { } batch)
    {
        PrintBatch(batch);
    }
}

void PrintBatch(RecordBatch batch)
{
    var vendorId = batch.Column(0) as Int32Array;
    var pickupDatetime = batch.Column(1) as TimestampArray;
    var fareAmount = batch.Column(2) as DoubleArray;

    for (int i = 0; i < batch.Length; i++)
    {
        var vendor = vendorId?.GetValue(i)?.ToString(CultureInfo.InvariantCulture) ?? "NULL";

        var datetime = "NULL";
        if (pickupDatetime != null && !pickupDatetime.IsNull(i))
        {
            var timestamp = pickupDatetime.GetTimestamp(i);
            if (timestamp.HasValue)
            {
                datetime = timestamp.Value.ToString("yyyy-MM-dd HH:mm:ss", CultureInfo.InvariantCulture);
            }
        }

        var fare = fareAmount?.GetValue(i)?.ToString("F2", CultureInfo.InvariantCulture) ?? "NULL";

        Console.WriteLine($"VendorID: {vendor}, tpep_pickup_datetime: {datetime}, fare_amount: {fare}");
    }
}
