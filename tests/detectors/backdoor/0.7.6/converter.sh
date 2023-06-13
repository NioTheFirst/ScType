#!/bin/bash

input_file="$1"
output_file="$2"

# Check if both input and output files are provided
if [[ -z "$input_file" || -z "$output_file" ]]; then
    echo "Usage: $0 <input_file> <output_file>"
    exit 1
fi

# Check if the input file exists
if [[ ! -f "$input_file" ]]; then
    echo "Input file '$input_file' does not exist."
    exit 1
fi

line_count=0
concatenated_lines=""

while IFS= read -r line; do
    line_count=$((line_count + 1))
    concatenated_lines+="$line"

    # Add comma if not the last line in a group of 5
    if ((line_count % 5 != 0)); then
        concatenated_lines+=","
    fi

    # Add newline if the last line in a group of 5
    if ((line_count % 5 == 0)); then
        concatenated_lines="[t],$concatenated_lines"  # Append "[t]," to the beginning
        echo "$concatenated_lines" >> "$output_file"
        concatenated_lines=""
    fi
done < "$input_file"

# Append the remaining lines if not a multiple of 5
if [[ -n "$concatenated_lines" ]]; then
    echo "$concatenated_lines" >> "$output_file"
fi

echo "Modified text written to '$output_file'."

