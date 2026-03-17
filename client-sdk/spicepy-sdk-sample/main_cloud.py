from spicepy import Client


def main() -> None:
    api_key = "<YOUR_API_KEY>"
    flight_url = "grpc+tls://flight.spiceai.io:443"

    client = Client(api_key=api_key, flight_url=flight_url)
    data = client.query("show tables;", timeout=5 * 60)
    print(data.read_pandas())


if __name__ == "__main__":
    main()
