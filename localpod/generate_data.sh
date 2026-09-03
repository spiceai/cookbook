#!/bin/bash

set -euo pipefail

# Set the output file name
output_file="data.csv"
temporary_file=$(mktemp "${output_file}.XXXXXX")
trap 'rm -f "$temporary_file"' EXIT

# Number of rows to generate
num_rows=1000

# Write the header to the file
printf 'timestamp,val1,val2\n' > "$temporary_file"

# Loop to generate each row
for ((i=1; i<=num_rows; i++))
do
    # Get the current timestamp
    timestamp=$(date +"%Y-%m-%d %H:%M:%S")

    # Generate deterministic values for val1 and val2
    val1=$((i % 100))
    val2=$(((i * 7) % 100))

    # Write the row to the CSV file
    printf '%s,%d,%d\n' "$timestamp" "$val1" "$val2" >> "$temporary_file"

    # Optional: Add a sleep to delay each row generation by 1 second
    # sleep 1
done

chmod 0644 "$temporary_file"
mv "$temporary_file" "$output_file"
trap - EXIT

echo "CSV file generated: $output_file"
