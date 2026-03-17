using Spice;
using System.Threading.Tasks;
using System;

public class Cloud
{
	public static async Task Main(string[] args)
	{
		var apiKey = Environment.GetEnvironmentVariable("SPICE_API_KEY");
		if (string.IsNullOrWhiteSpace(apiKey))
		{
			Console.Error.WriteLine("Set SPICE_API_KEY before running this sample.");
			Environment.Exit(1);
		}

		var httpAddress = Environment.GetEnvironmentVariable("SPICE_HTTP_URL") ?? "https://data.spiceai.io";
		var flightAddress = Environment.GetEnvironmentVariable("SPICE_FLIGHT_URL") ?? "flight.spiceai.io:443";

		var client = new SpiceClientBuilder()
            .WithApiKey(apiKey)
            .WithHttpAddress(httpAddress)
            .WithFlightAddress(flightAddress)
            .WithTls(true)
			.Build();

		var data = await client.Query("show tables;");
		await foreach (var batch in data)
		{
			Console.WriteLine(batch);
		}
	}
}
