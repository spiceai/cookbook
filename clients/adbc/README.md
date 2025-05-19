# Python ADBC Client with Parameterized Queries

This repository provides a simple cookbook example demonstrating how to use Python to query Spice via the Apache Arrow Database Connectivity (ADBC) API with the Flight SQL interface to Spice OSS. The example script connects to a local Spice OSS runtime, executes a parameterized query and a simple query, and fetches results as Arrow Tables.

## Requirements

- Python 3.8+
- [Spice CLI](https://docs.spiceai.org/getting-started) installed and Spice OSS runtime available
- [pip](https://pip.pypa.io/en/stable/)

## Recipe Steps

### 1. Clone this repository

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/clients/adbc
```

### 2. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Start Spice OSS

In a separate terminal, start the Spice OSS runtime:

```bash
spice run
```

### 4. Execute the ADBC client script

In a new terminal (with the virtual environment activated):

```bash
python3 main.py
```

Expected output:

```
pyarrow.Table
AccountId: string
ServiceId: string
AddOnSid: string
AddOnTypeSid: string
AddOnJson: string
DateCreated: timestamp[s]
DateUpdated: timestamp[s]
----
AccountId: [["account123","account789","account456"]]
ServiceId: [["service789","service789","service789"]]
AddOnSid: [["addon3","addon7","addon10"]]
AddOnTypeSid: [["type123","type123","type789"]]
AddOnJson: [["{\feature\":\"voice_integration\"}"","{\feature\":\"voice_integration\"}"","{\feature\":\"mms_support\"}""]]
DateCreated: [[2025-04-03 15:45:00,2025-04-07 11:30:00,2025-04-10 09:45:00]]
DateUpdated: [[2025-04-03 15:45:00,2025-04-07 11:30:00,2025-04-10 09:45:00]]
```

## Learn more

- [Spice OSS Documentation](https://docs.spiceai.org/)
- [Apache Arrow ADBC Python API](https://arrow.apache.org/adbc/main/python/)
- [Flight SQL Interface](https://arrow.apache.org/docs/format/Flight.html)
