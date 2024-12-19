#!/bin/bash

# Set the output file name
output_file="data.csv"

# Number of rows to generate
num_rows=1000

# Write the header to the file
if [ ! -f "$output_file" ]; then
    echo "timestamp,val1,val2\n" > "$output_file"
fi

# Loop to generate each row
for ((i=1; i<=num_rows; i++))
do
    # Get the current timestamp
    timestamp=$(date +"%Y-%m-%d %H:%M:%S")

    # Generate random values for val1 and val2
    val1=$((RANDOM % 100))
    val2=$((RANDOM % 100))

    # Write the row to the CSV file
    echo "$timestamp,$val1,$val2" >> "$output_file"

    # Optional: Add a sleep to delay each row generation by 1 second
    # sleep 1
done

echo "CSV file generated: $output_file"