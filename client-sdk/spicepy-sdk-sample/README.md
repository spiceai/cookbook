# Spice with spicepy SDK

This recipe demonstrates how to use the Spice Python SDK to connect to a Spice runtime and query data.

## Prerequisites

This recipe requires [Python](https://www.python.org/) to be installed.

## Start spice runtime

```shell
spice run
```

## Install dependencies

```shell
python -m venv .venv
source .venv/bin/activate
pip install git+https://github.com/spiceai/spicepy@v2.0.0
```

## Run sample application

```shell
python sample.py
```

Results:

```shell
➜ python sample.py 
   trip_distance  total_amount
0      312722.30         22.15
1       97793.92         36.31
2       82015.45         21.56
3       72975.97         20.04
4       71752.26         49.57
5       59282.45         33.52
6       59076.43         23.17
7       58298.51         18.63
8       51619.36         24.20
9       44018.64         52.43
```
