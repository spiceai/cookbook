# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "spicepy",
#     "adbc-driver-flightsql",
#     "adbc-driver-manager",
# ]
#
# [tool.uv.sources]
# spicepy = { git = "https://github.com/spiceai/spicepy", rev = "v3.1.0" }
# ///
from spicepy import Client

def main():
    client = Client()

    print("=== Using query ===")
    query_with_sql(client)

    print("\n=== Using query with params ===")
    query_with_sql_params(client, 5)

def query_with_sql(client: Client):
    data = client.query(
        'SELECT "VendorID", "tpep_pickup_datetime", "fare_amount" FROM taxi_trips LIMIT 10'
    )

    for chunk in data:
        batch = chunk.data
        for i in range(batch.num_rows):
            print(
                f"VendorID: {batch['VendorID'][i].as_py()}, "
                f"tpep_pickup_datetime: {batch['tpep_pickup_datetime'][i].as_py()}, "
                f"fare_amount: {batch['fare_amount'][i].as_py()}"
            )


def query_with_sql_params(client: Client, limit: int):
    data = client.query_with_params(
        'SELECT "VendorID", "tpep_pickup_datetime", "fare_amount" FROM taxi_trips LIMIT $1',
        params=[limit],
    )

    for batch in data:
        for i in range(batch.num_rows):
            print(
                f"VendorID: {batch['VendorID'][i].as_py()}, "
                f"tpep_pickup_datetime: {batch['tpep_pickup_datetime'][i].as_py()}, "
                f"fare_amount: {batch['fare_amount'][i].as_py()}"
            )

if __name__ == "__main__":
    main()
