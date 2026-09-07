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

client = Client(
    api_key='API_KEY',
    flight_url="grpc+tls://flight.spiceai.io"
)
data = client.query('show tables;', timeout=5*60)
pd = data.read_pandas()

print(pd)
