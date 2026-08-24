# Shared Sample Data

Data files referenced by multiple recipes, usually via a relative path such as
`file:../data/customer_feedback.csv`.

| Path                             | Description                                                                                  |
| -------------------------------- | -------------------------------------------------------------------------------------------- |
| `customer_feedback.csv`          | Short customer feedback statements, used by the AI and sentiment recipes.                     |
| `taxi_zone_lookup.csv`           | NYC TLC taxi zone lookup table.                                                              |
| `taxi_trips/taxi_trips.parquet`  | 100,000 NYC yellow taxi trips from January 2024.                                             |

The `dremio` and `federation` recipes mount this directory into their local Dremio
container and expose it as a Dremio source named `datasets`, where the `taxi_trips`
folder becomes the physical dataset `datasets.taxi_trips`.

## Regenerating `taxi_trips/taxi_trips.parquet`

An even sample (every 27th row) of the [NYC TLC January 2024 yellow taxi
trips](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page), restricted to
rows with a plausible passenger count, distance, and fare, and reduced to the six
columns the recipes query. Regenerate it with [DuckDB](https://duckdb.org):

```sql
LOAD httpfs;
COPY (
  WITH sane AS (
    SELECT
      tpep_pickup_datetime AS pickup_datetime,
      CAST(passenger_count AS BIGINT) AS passenger_count,
      trip_distance AS trip_distance_mi,
      fare_amount,
      tip_amount,
      total_amount,
      row_number() OVER (ORDER BY tpep_pickup_datetime, total_amount, trip_distance, fare_amount) AS rn
    FROM read_parquet('https://spiceai-demo-datasets.s3.us-east-1.amazonaws.com/taxi_trips/2024/yellow_tripdata_2024-01.parquet')
    WHERE passenger_count BETWEEN 1 AND 6
      AND tpep_pickup_datetime >= TIMESTAMP '2024-01-01' AND tpep_pickup_datetime < TIMESTAMP '2024-02-01'
      AND trip_distance > 0 AND fare_amount > 0 AND total_amount > 0 AND tip_amount >= 0
  )
  SELECT pickup_datetime, passenger_count, trip_distance_mi, fare_amount, tip_amount, total_amount
  FROM sane WHERE rn % 27 = 0 ORDER BY rn LIMIT 100000
) TO 'taxi_trips/taxi_trips.parquet' (FORMAT PARQUET, COMPRESSION SNAPPY, ROW_GROUP_SIZE 100000);
```

Keep `taxi_trips/` free of non-Parquet files — Dremio promotes the whole folder as a
single Parquet dataset.
