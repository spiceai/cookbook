package ai.spice.example;

import java.net.URI;

import org.apache.arrow.flight.FlightStream;
import org.apache.arrow.vector.VectorSchemaRoot;

import ai.spice.SpiceClient;

public class Cloud {
    public static void main(String[] args) {
        try (
            SpiceClient client = SpiceClient.builder()
                .withApiKey("API_KEY")
                .withHttpAddress(URI.create("https://data.spiceai.io"))
                .withFlightAddress(URI.create("grpc+tls://flight.spiceai.io:443"))
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
