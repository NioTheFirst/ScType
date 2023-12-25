#!/bin/bash
# Replace "file.txt" with the path to your file
file_path="Utils_types.txt"

# Use grep to count occurrences of "-1,-1" in the file
occurrences=$(grep -c "-1,-1" "$file_path")

# Print the number of occurrences
echo "Number of occurrences: $occurrences"

