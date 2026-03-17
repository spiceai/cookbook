# Install with: pip install git+https://github.com/spiceai/spicepy
from spicepy import Client

client = Client(
    api_key='API_KEY',
    flight_url="grpc+tls://flight.spiceai.io"
)
data = client.query('show tables;', timeout=5*60)
pd = data.read_pandas()

print(pd)
