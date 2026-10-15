package ai.spice.example;

import java.net.URI;

import org.apache.arrow.flight.FlightStream;
import org.apache.arrow.vector.VectorSchemaRoot;

import ai.spice.SpiceClient;

public class Cloud {
    public static void main(String[] args) {
        String apiKey = System.getenv("SPICE_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            System.err.println("Set the SPICE_API_KEY environment variable to your Spice.ai Cloud API key.");
            System.exit(1);
        }

        try (
            SpiceClient client = SpiceClient.builder()
                .withApiKey(apiKey)
                .withHttpAddress(URI.create("https://us-east-1-prod-aws-data.spiceai.io"))
                .withFlightAddress(URI.create("grpc+tls://us-east-1-prod-aws-flight.spiceai.io"))
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
