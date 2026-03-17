package ai.spice.example;

import java.net.URI;

import org.apache.arrow.flight.FlightStream;
import org.apache.arrow.vector.VectorSchemaRoot;

import ai.spice.SpiceClient;

public class Cloud {
    public static void main(String[] args) {
        String apiKey = System.getenv("SPICE_API_KEY");
        if (apiKey == null || apiKey.isBlank()) {
            System.err.println("Set SPICE_API_KEY before running this sample.");
            System.exit(1);
        }

        String httpUrl = System.getenv().getOrDefault("SPICE_HTTP_URL", "https://data.spiceai.io");
        String flightUrl = System.getenv().getOrDefault("SPICE_FLIGHT_URL", "grpc+tls://flight.spiceai.io:443");

        try (
            SpiceClient client = SpiceClient.builder()
                .withApiKey(apiKey)
                .withHttpAddress(URI.create(httpUrl))
                .withFlightAddress(URI.create(flightUrl))
                .build()
        ) {
            FlightStream stream = client.query(
                "show tables;"
            );

            while (stream.next()) {
                try (VectorSchemaRoot batches = stream.getRoot()) {
                    System.out.println(batches.contentToTSVString());
                }
            }
        } catch (Exception e) {
            System.err.println("An unexpected error occurred: " + e.getMessage());
        }
    }
}
