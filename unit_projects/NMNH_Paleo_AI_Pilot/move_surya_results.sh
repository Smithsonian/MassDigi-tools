#!/bin/bash

# Loop through all directories in the current path
for dir in */; do
    # Remove trailing slash from directory name
    folder_name=$(basename "$dir")
    
    # Check if results.json exists in the folder
    if [ -f "$dir/results.json" ]; then
        # Attempt to move and rename results.json to current directory
        if mv "$dir/results.json" "./${folder_name}.json"; then
            echo "Successfully moved and renamed $dir/results.json"
        else
            echo "Error: Failed to move $dir/results.json"
            exit
        fi
    else
        echo "No results.json found in $dir"
        exit
    fi
done