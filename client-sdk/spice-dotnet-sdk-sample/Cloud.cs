using Spice;
using System.Threading.Tasks;

public class Cloud
{
	public static async Task Main(string[] args)
	{
		var client = new SpiceClientBuilder()
            .WithSpiceCloud("API_KEY")
			.Build();
		var data = await client.Query("show tables;");
	}
}
