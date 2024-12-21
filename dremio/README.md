
# Dremio Data Connector

The Dremio recipe uses a publicly accessible demo instance of Dremio loaded with sample datasets. Thus, setting up your own Dremio instance is not required to complete the recipe, but the same steps can be used to connect to any Dremio instance.

**Step 1.** Initialize a Spice project:

```bash
spice init dremio-demo
cd dremio-demo
```

**Step 2.** Set the login credentials that the Spice runtime will use when accessing Dremio. Ensure this command is run in the `dremio-demo` directory.

```bash
spice login dremio -u demo -p demo1234
```

**Step 3.** Start the runtime.

```bash
spice run
```

**Step 4.** Configure the dataset to connect to Dremio:

In another terminal window in the `dremio-demo` folder:

```bash
cd dremio-demo
spice dataset configure
```

Enter the name of the dataset:

```bash
dataset name: (dremio-demo)  taxi_trips
```

Enter the description of the dataset:

```bash
description: taxi trips data in Dremio
```

Specify the location of the dataset:

```bash
from: dremio:datasets.taxi_trips
```

Specify the Dremio endpoint:

```bash
endpoint: grpc://20.163.171.8:32010
```

Select "y" when prompted whether to locally accelerate the dataset:

```bash
Locally accelerate (y/n)? y
```

The CLI will confirm the dataset has been configured with the following output:

```bash
Saved datasets/taxi_trips/dataset.yaml
```

And the content of dataset.yaml is the following:

```yaml
from: dremio:datasets.taxi_trips
name: taxi_trips
description: taxi trips data in Dremio
params:
  dremio_endpoint: grpc://20.163.171.8:32010
acceleration:
  enabled: true
  refresh_check_interval: 10s
  refresh_mode: full
```

The Spice runtime terminal will show that the dataset has been loaded:

```bash
2024-08-05T05:04:16.524586Z  INFO runtime: Dataset taxi_trips registered (dremio:datasets.taxi_trips), acceleration (arrow, 10s refresh), results cache enabled.
2024-08-05T05:04:16.526366Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2024-08-05T05:04:18.915971Z  INFO runtime::accelerated_table::refresh_task: Loaded 100,000 rows (27.91 MiB) for dataset taxi_trips in 2s 389ms.
```

**Step 5.** Run queries against the dataset using the Spice SQL REPL.

In a new terminal, start the Spice SQL REPL.

```bash
spice sql
```

Now query `taxi_trips`:

```sql
sql> select avg(total_amount), avg(tip_amount), count(1), passenger_count from taxi_trips group by passenger_count order by passenger_count asc;
+------------------------------+----------------------------+-----------------+-----------------+
| avg(taxi_trips.total_amount) | avg(taxi_trips.tip_amount) | count(Int64(1)) | passenger_count |
+------------------------------+----------------------------+-----------------+-----------------+
| 23.2                         | 3.8666666666666667         | 3               | 0               |
| 15.394881909237037           | 1.9225555830345065         | 80870           | 1               |
| 17.714222499449637           | 1.967968738533792          | 13627           | 2               |
| 17.441359661495056           | 1.7930070521861776         | 3545            | 3               |
| 17.219515789473686           | 1.3453947368421055         | 1900            | 4               |
| 21.122631578947367           | 1.36                       | 38              | 5               |
| 22.401176470588236           | 2.764705882352941          | 17              | 6               |
+------------------------------+----------------------------+-----------------+-----------------+

Time: 0.03241875 seconds. 7 rows.
```

**Next Steps**
This recipe accelerates query performance using [Spice Data Accelerators](https://docs.spiceai.org/data-accelerators).  Experiment with different acceleration options by editing the dataset.yaml file or removing acceleration altogether to have the Spice runtime federate the query to Dremio directly.
