#!/bin/bash

for file in \[*\]log.csv; do
    # Remove all square brackets and replace remaining colons with dashes
    clean_name="${file//[\[\]]/}"
    clean_name="${clean_name/_/-}"

    # Ensure the file name pattern matches something like '2024-05-07_22-50log.csv'
    # This assumes the first segment is a date and the next segment after underscore is a time
    new_file="${clean_name%log.csv}log.csv"

    # Rename the file
    mv "$file" "$new_file"
done
