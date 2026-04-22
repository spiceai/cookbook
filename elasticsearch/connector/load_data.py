#!/usr/bin/env python3
"""
Load articles.parquet into Elasticsearch.

Usage:
  uv run load_data.py
  uv run load_data.py --all-types
  uv run load_data.py --parquet articles.parquet --all-types
"""

import argparse
import json
import os
import sys
import time

import pyarrow.parquet as pq
import requests

parser = argparse.ArgumentParser()
parser.add_argument(
    "--es-host", default=os.environ.get("ES_HOST", "http://localhost:9200")
)
parser.add_argument("--es-user", default=os.environ.get("ES_USER", "elastic"))
parser.add_argument("--es-pass", default=os.environ.get("ES_PASS", "spiceai"))
parser.add_argument("--parquet", default="articles.parquet")
parser.add_argument("--index", default="articles")
parser.add_argument(
    "--all-types",
    action="store_true",
    help="Also create and load the all_types index covering every ES field type",
)
parser.add_argument("--all-types-index", default="all_types")
parser.add_argument("--all-types-docs", type=int, default=10)
args = parser.parse_args()

ES_HOST = args.es_host
ES_AUTH = (args.es_user, args.es_pass) if args.es_user else None
INDEX = args.index
PARQUET_PATH = args.parquet


# ---------------------------------------------------------------------------
# Wait for Elasticsearch
# ---------------------------------------------------------------------------
def wait_for_es(retries: int = 30, delay: int = 5) -> None:
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(f"{ES_HOST}/_cluster/health", auth=ES_AUTH, timeout=5)
            status = r.json().get("status", "red")
            if status in ("green", "yellow"):
                print(f"Elasticsearch ready (status={status})")
                return
            print(
                f"[{attempt}/{retries}] Cluster status: {status}, retrying in {delay}s …"
            )
        except Exception as exc:
            print(f"[{attempt}/{retries}] Not ready ({exc}), retrying in {delay}s …")
        time.sleep(delay)
    print("ERROR: Elasticsearch did not become healthy in time.")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Articles index
# ---------------------------------------------------------------------------
ARTICLES_MAPPING = {
    "settings": {"number_of_shards": 1, "number_of_replicas": 0},
    "mappings": {
        "properties": {
            "id": {"type": "integer"},
            "title": {
                "type": "text",
                "analyzer": "english",
                "fields": {"keyword": {"type": "keyword"}},
            },
            "content": {"type": "text", "analyzer": "english"},
            "author": {"type": "keyword"},
            "category": {"type": "keyword"},
            "tags": {
                "type": "text",
                "analyzer": "english",
                "fields": {"keyword": {"type": "keyword"}},
            },
            "published_at": {
                "type": "date",
                "format": "strict_date_time_no_millis||strict_date_optional_time",
            },
            "views": {"type": "integer"},
            "likes": {"type": "integer"},
        }
    },
}


def recreate_index(name: str, mapping: dict) -> None:
    url = f"{ES_HOST}/{name}"
    if requests.head(url, auth=ES_AUTH).status_code == 200:
        print(f"Index '{name}' already exists — deleting for a clean load.")
        requests.delete(url, auth=ES_AUTH).raise_for_status()
    requests.put(url, json=mapping, auth=ES_AUTH).raise_for_status()
    print(f"Index '{name}' created.")


def bulk_request(lines: list[str]) -> None:
    body = "\n".join(lines) + "\n"
    r = requests.post(
        f"{ES_HOST}/_bulk",
        data=body.encode(),
        headers={"Content-Type": "application/x-ndjson"},
        auth=ES_AUTH,
        timeout=120,
    )
    r.raise_for_status()
    errors = [
        item for item in r.json().get("items", []) if "error" in item.get("index", {})
    ]
    if errors:
        print(f"  WARNING: {len(errors)} bulk errors — first: {errors[0]}")


def load_articles(df: dict) -> None:
    n = len(df["id"])
    lines = []
    for i in range(n):
        doc = {col: df[col][i] for col in df}
        lines.append(json.dumps({"index": {"_index": INDEX, "_id": doc["id"]}}))
        lines.append(json.dumps(doc))
    bulk_request(lines)
    requests.post(f"{ES_HOST}/{INDEX}/_refresh", auth=ES_AUTH)
    count = (
        requests.get(f"{ES_HOST}/{INDEX}/_count", auth=ES_AUTH).json().get("count", "?")
    )
    print(f"Loaded {n} documents → '{INDEX}' (count={count})")


# ---------------------------------------------------------------------------
# all_types index — one document per supported ES field type
# ---------------------------------------------------------------------------
ALL_TYPES_MAPPING = {
    "settings": {"number_of_shards": 1, "number_of_replicas": 0},
    "mappings": {
        "properties": {
            # Core scalar types
            "id": {"type": "integer"},
            "field_text": {"type": "text", "analyzer": "standard"},
            "field_keyword": {"type": "keyword"},
            "field_long": {"type": "long"},
            "field_integer": {"type": "integer"},
            "field_short": {"type": "short"},
            "field_byte": {"type": "byte"},
            "field_double": {"type": "double"},
            "field_float": {"type": "float"},
            "field_half_float": {"type": "half_float"},
            "field_scaled_float": {"type": "scaled_float", "scaling_factor": 100},
            "field_unsigned_long": {"type": "unsigned_long"},
            # Boolean
            "field_boolean": {"type": "boolean"},
            # Date / time
            "field_date": {"type": "date", "format": "strict_date_optional_time"},
            "field_date_nanos": {"type": "date_nanos"},
            # Binary
            "field_binary": {"type": "binary"},
            # Range types
            "field_integer_range": {"type": "integer_range"},
            "field_long_range": {"type": "long_range"},
            "field_float_range": {"type": "float_range"},
            "field_double_range": {"type": "double_range"},
            "field_date_range": {
                "type": "date_range",
                "format": "strict_date_optional_time",
            },
            # Structured / complex types
            "field_object": {
                "type": "object",
                "properties": {
                    "name": {"type": "keyword"},
                    "value": {"type": "integer"},
                },
            },
            "field_nested": {
                "type": "nested",
                "properties": {
                    "tag": {"type": "keyword"},
                    "score": {"type": "float"},
                },
            },
            # Geo types
            "field_geo_point": {"type": "geo_point"},
            "field_geo_shape": {"type": "geo_shape"},
            # Specialised text types
            "field_ip": {"type": "ip"},
            "field_version": {"type": "version"},
            # Completion / search-as-you-type
            "field_completion": {"type": "completion"},
            "field_search_as_you_type": {"type": "search_as_you_type"},
            # Token count
            "field_token_count": {
                "type": "token_count",
                "analyzer": "standard",
            },
            # Dense vector (small dim for speed)
            "field_dense_vector": {
                "type": "dense_vector",
                "dims": 4,
                "index": True,
                "similarity": "cosine",
            },
            # Flattened
            "field_flattened": {"type": "flattened"},
        }
    },
}

import base64
import math
import random


def _make_all_types_doc(i: int) -> dict:
    """Return a single document exercising every mapped field type."""
    rng = random.Random(i)
    ts = f"2024-0{(i % 9) + 1}-{(i % 28) + 1:02d}T{i % 24:02d}:00:00Z"
    return {
        "id": i,
        "field_text": f"The quick brown fox jumps over the lazy dog — document {i}",
        "field_keyword": f"category_{i % 5}",
        "field_long": rng.randint(-(2**40), 2**40),
        "field_integer": rng.randint(-100_000, 100_000),
        "field_short": rng.randint(-32768, 32767),
        "field_byte": rng.randint(-128, 127),
        "field_double": rng.uniform(-1e6, 1e6),
        "field_float": float(round(rng.uniform(-1000, 1000), 4)),
        "field_half_float": float(round(rng.uniform(-100, 100), 2)),
        "field_scaled_float": float(round(rng.uniform(0, 999.99), 2)),
        "field_unsigned_long": rng.randint(0, 2**60),
        "field_boolean": bool(i % 2),
        "field_date": ts,
        "field_date_nanos": ts.replace("Z", ".000000000Z"),
        "field_binary": base64.b64encode(f"binary_payload_{i}".encode()).decode(),
        "field_integer_range": {"gte": i * 10, "lte": i * 10 + 5},
        "field_long_range": {"gte": i * 1000, "lte": i * 1000 + 100},
        "field_float_range": {"gte": float(i), "lte": float(i) + 0.5},
        "field_double_range": {"gte": float(i) * 1.1, "lte": float(i) * 1.1 + 0.01},
        "field_date_range": {
            "gte": f"2024-01-{(i % 28) + 1:02d}T00:00:00Z",
            "lte": f"2024-12-{(i % 28) + 1:02d}T23:59:59Z",
        },
        "field_object": {"name": f"obj_{i}", "value": i * 7},
        "field_nested": [
            {"tag": f"tag_{j}", "score": float(round(rng.uniform(0, 1), 3))}
            for j in range(1, 3)
        ],
        "field_geo_point": {
            "lat": round(rng.uniform(-90, 90), 6),
            "lon": round(rng.uniform(-180, 180), 6),
        },
        "field_geo_shape": {
            "type": "Point",
            "coordinates": [
                round(rng.uniform(-180, 180), 6),
                round(rng.uniform(-90, 90), 6),
            ],
        },
        "field_ip": f"192.168.{i % 256}.{(i * 7) % 256}",
        "field_version": f"1.{i}.0",
        "field_completion": {"input": [f"suggest_{i}", f"doc_{i}"], "weight": i + 1},
        "field_search_as_you_type": f"searchable text for document number {i}",
        # token_count is computed by ES; send the source text
        "field_token_count": f"token count source text document {i}",
        "field_dense_vector": [round(math.sin(i + j), 6) for j in range(4)],
        "field_flattened": {"arbitrary_key": f"value_{i}", "nested_key": {"deep": i}},
    }


def load_all_types(n: int = 10) -> None:
    recreate_index(args.all_types_index, ALL_TYPES_MAPPING)
    lines = []
    for i in range(1, n + 1):
        doc = _make_all_types_doc(i)
        lines.append(json.dumps({"index": {"_index": args.all_types_index, "_id": i}}))
        lines.append(json.dumps(doc))
    bulk_request(lines)
    requests.post(f"{ES_HOST}/{args.all_types_index}/_refresh", auth=ES_AUTH)
    count = (
        requests.get(f"{ES_HOST}/{args.all_types_index}/_count", auth=ES_AUTH)
        .json()
        .get("count", "?")
    )
    print(f"Loaded {n} documents → '{args.all_types_index}' (count={count})")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    wait_for_es()

    print(f"Reading {PARQUET_PATH} …")
    df = pq.read_table(PARQUET_PATH).to_pydict()

    recreate_index(INDEX, ARTICLES_MAPPING)
    load_articles(df)

    if args.all_types:
        load_all_types(args.all_types_docs)

    print("Done.")
