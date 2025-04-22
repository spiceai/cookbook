# ADBC API Cookbook for Spice.ai

This repository provides a simple cookbook example demonstrating how to use the Apache Arrow Database Connectivity (ADBC) API with the Flight SQL interface to Spice OSS. The example script connects to a local Spice OSS runtime, executes a parameterized query and a simple query, and fetches results as Arrow Tables.

## Recipe Steps

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start Spice OSS
```bash
spice run
```

### Execute ADBC client script
In a new terminal,

```bash
python3 main.py
```

Expected output:
```
pyarrow.Table
the_answer: int64 not null
----
the_answer: [[42]]
pyarrow.Table
one: int64 not null
----
one: [[1]]
```

