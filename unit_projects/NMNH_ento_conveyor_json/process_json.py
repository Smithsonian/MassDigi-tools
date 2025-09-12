#!/usr/bin/env python3
#
# Get JSON files and ingest the IRN contents to database
#  v. 2025-09-04
#

import sys
import os
from time import strftime
from time import localtime
from pathlib import Path
import pandas as pd


if len(sys.argv) == 1:
    print("Path to drawer files missing")
    sys.exit(1)
elif len(sys.argv) == 2:
    json_path = sys.argv[1]
else:
    print("Wrong number of args")
    sys.exit(1)



def get_json_files(json_path):
    try:
        json_files = []
        for root, _, f_names in os.walk(json_path):
            for f in f_names:
                if Path(f).suffix.lower() == '.json':
                    json_files.append(os.path.join(root, f))
        return json_files
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


json_files = get_json_files(json_path)


outfile = "{}/json/{}.csv".format(json_path, os.path.split(json_path)[-1])
with open(outfile, "w") as f:
    f.write("specimen,damaged,digitized_by,digitized_on,double_sided_labels,drawer_id,drawer_name,insect_id,multi_insect,pin_content,remarks,size,sphere,state_change,tray_id,unable_to_scan_labels,unit_tray_id\n")
        

for json_file in json_files:
    specimen = Path(json_file).stem
    json_data = pd.read_json(json_file)
    json_data.drop('images', axis=1).drop_duplicates().to_csv(outfile, header=False, index=False, mode="a")

