FROM spiceai/spiceai:latest-models

# Copy the Spicepod configuration file
COPY spicepod.yaml /app/spicepod.yaml

# Copy the .env.local & .env files
COPY .env* /app/

# Spice runtime start-up arguments
CMD ["--http","0.0.0.0:8090","--metrics", "0.0.0.0:9090","--flight","0.0.0.0:50051"]

EXPOSE 8090
EXPOSE 9090
EXPOSE 50051

# Start the Spicepod