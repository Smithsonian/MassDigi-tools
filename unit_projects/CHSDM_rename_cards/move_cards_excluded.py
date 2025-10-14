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
            # If there a dupes in the source list
            if original_name in filelist:
                print(f"File was twice in list: {original_name}")
                with open("excluded_duperow.txt", "a") as f:
                    f.write(f"{original_name}\n")
                continue
            filelist.append(original_name)

            if original_path is None:
                print(f"File not found: {original_name}")
                with open("excluded_missing.txt", "a") as f:
                    f.write(f"{original_name}\n")
                continue
            else:
                # Do any file in the set of folders that match the filename
                # while original_path is not None:
                new_path = os.path.join(destination_folder, new_name)

                if original_path:
                    # Handle name collision in duplicates folder
                    if os.path.exists(new_path):
                        base, ext = os.path.splitext(new_name)
                        i = 1
                        while os.path.exists(new_path):
                            new_path = os.path.join(duplicates_folder, f"{base}_dupe{i}{ext}")
                            i += 1
                        
                        try:
                            shutil.move(original_path, new_path)
                            print(f"Duplicate moved: {original_name} → {new_path}")
                        except Exception as e:
                            print(f"Error moving file {original_name} to {new_name}: {e}")
                    else:
                        # New filename does not exist
                        try:
                            shutil.move(original_path, new_path)
                            print(f"File {original_name} renamed to {new_name} and moved to destination folder.")
                        except Exception as e:
                            print(f"Error moving file {original_name} to {new_name}: {e}")
                original_path = find_file(original_name, source_folder)

except FileNotFoundError:
    print(f"CSV file not found: {csv_file}")
except Exception as e:
    print(f"An error occurred while processing the CSV: {e}")
