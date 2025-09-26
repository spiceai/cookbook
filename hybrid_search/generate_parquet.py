#!/usr/bin/env python3

import sys
import json
import polars as pl
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='[info] %(message)s')
logger = logging.getLogger(__name__)

BATCH_SIZE = 250
PARQUET_FILE = "bluesky_posts.parquet"

def normalize_record(record, rkey=None):
    """Normalize record to ensure consistent schema"""
    # Flatten nested structures for consistency
    normalized = {}

    # Basic fields
    normalized['type'] = record.get('$type', '')

    # Parse timestamp
    created_at_str = record.get('createdAt', '')
    if created_at_str:
        try:
            # Parse ISO format timestamp and convert to datetime
            normalized['created_at'] = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
        except ValueError:
            normalized['created_at'] = None
    else:
        normalized['created_at'] = None

    normalized['text'] = record.get('text', '')
    normalized['rkey'] = rkey or ''

    # Handle langs array - convert to string
    langs = record.get('langs', [])
    normalized['langs'] = ','.join(langs) if langs else ''

    # Handle embed as JSON string if present
    if 'embed' in record:
        normalized['embed'] = json.dumps(record['embed'])
    else:
        normalized['embed'] = ''

    return normalized

def process_batch(records):
    """Process a batch of records and append to parquet file"""
    if not records:
        return

    # Normalize all records to ensure consistent schema
    normalized_records = [normalize_record(record['record'], record['rkey']) for record in records]

    # Create DataFrame from normalized records
    df = pl.DataFrame(normalized_records)

    # Check if parquet file exists
    parquet_path = Path(PARQUET_FILE)

    if parquet_path.exists():
        # Read existing file and ensure schema compatibility
        existing_df = pl.read_parquet(PARQUET_FILE)

        # Ensure new df has same columns as existing
        existing_columns = set(existing_df.columns)
        new_columns = set(df.columns)

        # Add missing columns to new df with empty values
        for col in existing_columns - new_columns:
            df = df.with_columns(pl.lit('').alias(col))

        # Add missing columns to existing df with empty values
        for col in new_columns - existing_columns:
            existing_df = existing_df.with_columns(pl.lit('').alias(col))

        # Ensure column order matches
        df = df.select(sorted(df.columns))
        existing_df = existing_df.select(sorted(existing_df.columns))

        combined_df = pl.concat([existing_df, df])
        combined_df.write_parquet(PARQUET_FILE)
    else:
        # Create new file
        df.write_parquet(PARQUET_FILE)

def main():
    logger.info(f"boot!")
    records = []
    total_count = 0

    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                full_json = json.loads(line)

                # Filter for only kind:commit and operation:create
                if full_json.get('kind') != 'commit':
                    continue

                if ('commit' not in full_json or
                    full_json['commit'].get('operation') != 'create' or
                    'record' not in full_json['commit']):
                    continue

                record = full_json['commit']['record']
                rkey = full_json['commit'].get('rkey', '')
                records.append({'record': record, 'rkey': rkey})

                if len(records) >= BATCH_SIZE:
                    process_batch(records)
                    total_count += len(records)
                    logger.info(f"INSERTED {len(records)} ROWS; TOTAL {total_count}")
                    records = []

            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON: {e}")
                continue

    except KeyboardInterrupt:
        logger.info("Interrupted by user")

    # Process remaining records
    if records:
        process_batch(records)
        total_count += len(records)
        logger.info(f"INSERTED {len(records)} ROWS; TOTAL {total_count}")

    logger.info(f"Processing complete. Total records: {total_count}")
    logger.info(f"Data saved to: {PARQUET_FILE}")

if __name__ == "__main__":
    main()