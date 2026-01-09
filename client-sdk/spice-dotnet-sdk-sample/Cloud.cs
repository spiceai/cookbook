using Spice;
using System.Threading.Tasks;

public class Cloud
{
	public static async Task Main(string[] args)
	{
		var client = new SpiceClientBuilder()
            .WithApiKey("API_KEY")
            .WithHttpAddress("https://data.spiceai.io")
            .WithFlightAddress("flight.spiceai.io:443")
            .WithTls(true)
			.Build();
		var data = await client.Query("show tables;");
	}
}
