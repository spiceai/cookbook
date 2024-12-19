# Spice with spice.js SDK Recipe

This recipe demonstrates how to use the Spice JavaScript SDK to connect to a Spice runtime and query data.

## Prerequisites

This recipe requires [Node.js](https://nodejs.org/) to be installed.

## Start spice runtime

```shell
spice run
```

Ensure the dataset `taxi_trips` to be loaded

```shell
2024-09-23T21:54:09.980654Z  INFO runtime: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (arrow, 10s refresh), results cache enabled.
2024-09-23T21:54:09.981827Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2024-09-23T21:55:10.491380Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,964,624 rows (421.71 MiB) for dataset taxi_trips in 109ms.
```

## Install dependencies

```shell
npm install
```

## Run sample application

```shell
npm start # or node index.mjs
```

Results:

```shell
npm start

> spice.js-sdk-sample@1.0.0 start
> node index.mjs

┌─────────┬──────────┬──────────────────────┬─────────────┐
│ (index) │ VendorID │ tpep_pickup_datetime │ fare_amount │
├─────────┼──────────┼──────────────────────┼─────────────┤
│    0    │    2     │    1705115889000     │    11.4     │
│    1    │    2     │    1705117978000     │    13.5     │
│    2    │    2     │    1705116362000     │    11.4     │
│    3    │    2     │    1705118024000     │    27.5     │
│    4    │    2     │    1705114708000     │    18.4     │
│    5    │    2     │    1705118064000     │    14.2     │
│    6    │    2     │    1705115215000     │    88.1     │
│    7    │    2     │    1705116146000     │     10      │
│    8    │    2     │    1705116079000     │    28.9     │
│    9    │    1     │    1705115615000     │    35.2     │
└─────────┴──────────┴──────────────────────┴─────────────┘
```
