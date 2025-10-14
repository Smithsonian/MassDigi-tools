#!/bin/bash

# Usage: ./split_files.sh /path/to/source /path/to/destination

SOURCE_DIR="consolidated"
DEST_DIR="split"
MAX_FILES=5000

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "Source directory does not exist."
  exit 1
fi

mkdir -p "$DEST_DIR"

# Counter for folders
folder_index=1
file_count=0

# Create initial subfolder
current_folder="$DEST_DIR/folder_$folder_index"
mkdir -p "$current_folder"

# Loop through files in source directory
for file in "$SOURCE_DIR"/*; do
  if [[ -f "$file" ]]; then
    if (( file_count >= MAX_FILES )); then
      ((folder_index++))
      current_folder="$DEST_DIR/folder_$folder_index"
      mkdir -p "$current_folder"
      file_count=0
    fi

    cp "$file" "$current_folder/"
    ((file_count++))
  fi
done

