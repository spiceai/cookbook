import os
import sys

from spicepy import Client


def main() -> None:
    api_key = os.getenv("SPICE_API_KEY")
    if not api_key:
        print("Set SPICE_API_KEY before running this sample.", file=sys.stderr)
        raise SystemExit(1)

    flight_url = os.getenv("SPICE_FLIGHT_URL", "grpc+tls://flight.spiceai.io:443")

    client = Client(api_key=api_key, flight_url=flight_url)
    data = client.query("show tables;", timeout=5 * 60)
    print(data.read_pandas())


if __name__ == "__main__":
    main()
