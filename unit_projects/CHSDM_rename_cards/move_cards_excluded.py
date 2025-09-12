#!/usr/bin/env python3
#

import os
import shutil
import csv

# Define paths
csv_file = 'excluded.csv'  # Replace with your actual CSV file name
source_folder = 'chsdm_cards'  # Folder where original files and subfolders are located
destination_folder = 'excluded'  # Folder to move renamed files
duplicates_folder = 'excluded_duplicates'  # Folder to store duplicates

# Create destination and duplicates folders if they don't exist
os.makedirs(destination_folder, exist_ok=True)
os.makedirs(duplicates_folder, exist_ok=True)

# Function to search for a file in all subdirectories
def find_file(filename, search_path):
    for root, dirs, files in os.walk(search_path):
        if filename in files:
            return os.path.join(root, filename)
    return None

filelist = []

# Read the CSV and process each file
try:
    with open(csv_file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            original_name, new_name = row
            original_path = find_file(original_name, source_folder)
            new_path = os.path.join(destination_folder, new_name)

            if original_name in filelist:
                print(f"File was twice in list: {original_name}")
                with open("excluded_duperow.txt", "a") as f:
                    f.write(f"{original_name}\n")
                continue
            filelist.append(original_name)

            if original_path:
                if os.path.exists(new_path):
                    # If file with new name already exists, move to duplicates folder
                    duplicate_path = os.path.join(duplicates_folder, new_name)
                    if os.path.exists(duplicate_path):
                        print(f"Duplicate already exists in duplicates folder: {new_name} ({duplicate_path}). Skipping move.")
                    else:
                        try:
                            shutil.move(original_path, duplicate_path)
                            print(f"Duplicate found: {new_name}, moved to duplicates folder.")
                        except Exception as e:
                            print(f"Error moving duplicate file {original_name} to duplicates folder: {e}")
                else:
                    try:
                        shutil.move(original_path, new_path)
                        print(f"File {original_name} renamed to {new_name} and moved to destination folder.")
                    except Exception as e:
                        print(f"Error moving file {original_name} to {new_name}: {e}")
            else:
                print(f"File not found: {original_name}")
                with open("excluded_missing.txt", "a") as f:
                    f.write(f"{original_name}\n")
except FileNotFoundError:
    print(f"CSV file not found: {csv_file}")
except Exception as e:
    print(f"An error occurred while processing the CSV: {e}")
