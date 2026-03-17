using Spice;
using System.Threading.Tasks;

public class Cloud
{
	public static async Task Main(string[] args)
	{
		var apiKey = "<YOUR_API_KEY>";
		var httpAddress = "https://data.spiceai.io";
		var flightAddress = "flight.spiceai.io:443";

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
