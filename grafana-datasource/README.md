# Adding Spice as a Grafana Datasource

This recipe will show how to configure a Grafana dashboard to use Spice as the data source using the [Infinity](https://grafana.com/docs/plugins/yesoreyeram-infinity-datasource/latest/) plugin.

## Prerequisites

This recipe requires [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) to be installed.

## Running the recipe

Clone the `spiceai/cookbook` repository and navigate to the `grafana-datasource` directory:

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/grafana-datasource
```

Run the following command to start the components in the Docker Compose file:

`make`

This will start the Spice runtime and Grafana server. The Spice runtime will load two datasets based on the parquet file in S3.

### Setup with Infinity Grafana plugin

Follow steps 1-3 from the previous section.

1. Select "State: All", and search for "Infinity". Install and click on "Add new data source".
   ![screenshot](./img/grafana-datasource-7.png)

1. Leave the default values and click on "Save & Test".
   ![screenshot](./img/grafana-datasource-8.png)

1. Click on "Build a dashboard" and add a new visualization. Select "Infinity" from the list of data sources.
1. Change "Method" to "POST" and "URL" to `http://spice:8090/v1/sql`. Add SQL query in body, using "Raw" mode:

   ```sql
   SELECT to_timestamp(tpep_dropoff_datetime), fare_amount FROM public.taxi_trips LIMIT 100
   ```

   Add the header `Accept: application/json` as well.

![screenshot](./img/grafana-datasource-9.png)

## Clean up

To stop and remove the Docker containers/volumes that were created, run:

`make clean`
