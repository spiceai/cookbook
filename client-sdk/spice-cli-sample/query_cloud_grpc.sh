# Install the Spice CLI
# https://docs.spiceai.org/getting-started
curl https://install.spiceai.org | /bin/bash

# Run a SQL query via Arrow Flight (gRPC)
spice sql --api-key API_KEY --flight-url flight.spiceai.io:443 \
  "SELECT * FROM my_dataset LIMIT 10"
