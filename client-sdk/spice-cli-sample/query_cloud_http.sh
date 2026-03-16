# Install the Spice CLI
# https://docs.spiceai.org/getting-started
curl https://install.spiceai.org | /bin/bash

# Run a SQL query via HTTP
spice sql --api-key API_KEY --http-url https://data.spiceai.io \
  "SELECT * FROM my_dataset LIMIT 10"
