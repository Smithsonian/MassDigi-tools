#!/usr/bin/env python3

import os
import shutil


def move_jpgs(source_dir, target_dir, duplicates_dir):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    if not os.path.exists(duplicates_dir):
        os.makedirs(duplicates_dir)

    seen_filenames = set()

    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith(".jpg"):
                src_path = os.path.join(root, file)

                if file in seen_filenames:
                    # Duplicate filename found
                    dup_path = os.path.join(duplicates_dir, file)

                    # Handle name collision in duplicates folder
                    if os.path.exists(dup_path):
                        base, ext = os.path.splitext(file)
                        i = 1
                        while os.path.exists(dup_path):
                            dup_path = os.path.join(duplicates_dir, f"{base}_{i}{ext}")
                            i += 1

                    shutil.move(src_path, dup_path)
                    print(f"Duplicate moved: {src_path} → {dup_path}")
                else:
                    # Unique filename
                    seen_filenames.add(file)
                    dest_path = os.path.join(target_dir, file)

                    # Handle name collision in target folder
                    if os.path.exists(dest_path):
                        base, ext = os.path.splitext(file)
                        i = 1
                        while os.path.exists(dest_path):
                            dest_path = os.path.join(target_dir, f"{base}_{i}{ext}")
                            i += 1

                    shutil.move(src_path, dest_path)
                    print(f"Moved: {src_path} → {dest_path}")



# Define paths
source_directory = 'chsdm_cards'  # Folder where original files and subfolders are located
target_directory = 'consolidated'  # Folder to move renamed files
duplicates_directory = 'duplicates'  # Folder to st

move_jpgs(source_directory, target_directory, duplicates_directory)

