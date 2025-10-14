#!/usr/bin/env python3

import os
import shutil


# Define paths
source_folder = 'chsdm_cards'  # Folder where original files and subfolders are located
target_directory = 'consolidated'  # Folder to move renamed files
duplicates_folder = 'duplicates_allrest'  # Folder to store duplicates

# Create destination and duplicates folders if they don't exist
os.makedirs(target_directory, exist_ok=True)
os.makedirs(duplicates_folder, exist_ok=True)


for root, _, files in os.walk(source_folder):
    for file in files:
        if file.lower().endswith(".jpg"):
            src_path = os.path.join(root, file)

            # Unique filename
            dest_path = os.path.join(target_directory, file)
            
            if os.path.exists(dest_path):
                # Duplicate filename found
                dup_path = os.path.join(duplicates_folder, file)

                # Handle name collision in duplicates folder
                if os.path.exists(dup_path):
                    base, ext = os.path.splitext(file)
                    i = 1
                    while os.path.exists(dup_path):
                        dup_path = os.path.join(duplicates_folder, f"{base}_dupe{i}{ext}")
                        i += 1

                try:
                    shutil.move(src_path, dup_path)
                    print(f"Duplicate moved: {src_path} → {dup_path}")
                except Exception as e:
                    print(f"Error moving file {src_path} to {dup_path}: {e}")
            else:
                try:
                    shutil.move(src_path, dest_path)
                    print(f"Moved: {src_path} → {dest_path}")
                except Exception as e:
                    print(f"Error moving file {src_path} to {dest_path}: {e}")

