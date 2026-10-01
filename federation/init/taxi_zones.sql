-- Runs automatically on the container's first start via /docker-entrypoint-initdb.d.
-- Loads the NYC TLC taxi zone lookup table from the shared cookbook data directory.
CREATE TABLE taxi_zones (
    location_id  INTEGER NOT NULL,
    borough      TEXT NOT NULL,
    zone         TEXT NOT NULL,
    service_zone TEXT NOT NULL
);

COPY taxi_zones (location_id, borough, zone, service_zone)
FROM '/data/taxi_zone_lookup.csv' WITH (FORMAT csv, HEADER true);
