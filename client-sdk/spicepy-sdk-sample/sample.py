# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "spicepy",
# ]
#
# [tool.uv.sources]
# spicepy = { git = "https://github.com/spiceai/spicepy", rev = "v3.0.0" }
# ///
from spicepy import Client

client = Client()
data = client.query('SELECT trip_distance, total_amount FROM taxi_trips ORDER BY trip_distance DESC LIMIT 10;', timeout=5*60)
pd = data.read_pandas()
print(pd)
