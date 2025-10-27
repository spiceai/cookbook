# Adding Spice as a Grafana Datasource

This recipe will show how to configure a Grafana dashboard to use Spice as the data source using the [Infinity](https://grafana.com/docs/plugins/yesoreyeram-infinity-datasource/latest/) plugin.

## Prerequisites

This recipe requires [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) to be installed.

Install [`spice`](https://docs.spiceai.org/getting-started) locally so you can run the Spice runtime on your machine.

## Running the recipe

Clone the `spiceai/cookbook` repository and navigate to the `grafana-datasource` directory:

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/grafana-datasource
```

In one terminal, run the Spice runtime locally from this directory:

```bash
spice run
```

Spice will load the datasets defined in `spicepod.yaml` and listen on `localhost:8090`.

Open a second terminal and run the following command to start Grafana in Docker:

`make`

### Setup with Infinity Grafana plugin

1. Open Grafana in your browser at [http://localhost:3000](http://localhost:3000).
1. Log in with the default credentials `admin`/`admin`, skip the password change prompt.
![screenshot](./img/grafana-datasource-1.png)

1. Navigate to Administation -> Plugins and data -> Plugins.

1. Select "State: All", and search for "Infinity". Install and click on "Add new data source".
   ![screenshot](./img/grafana-datasource-7.png)

1. Leave the default values and click on "Save & Test".
   ![screenshot](./img/grafana-datasource-8.png)

1. Click on "Build a dashboard" and add a new visualization. Select "Infinity" from the list of data sources.
 - Change "Method" to "POST" and "URL" to `http://localhost:8090/v1/sql`.
 - Add SQL query in body, using "Raw" mode:

   ```sql
   SELECT to_timestamp(tpep_dropoff_datetime), fare_amount FROM public.taxi_trips LIMIT 100
   ```
- Add the header `Accept: application/json` as well.
- Set visualization to `Table`

![screenshot](./img/grafana-datasource-9.png)

## Clean up

Press `Ctrl+C` in the terminal running `spice run` to stop the Spice runtime.

To stop and remove the Docker containers/volumes that were created, run:

`make clean`
