#!/usr/bin/env python3
#
# Get folders from ASpace and store the RefIDs

import json
import requests
import csv
from time import time as unix 
from time import sleep

datafile = "files_w_damsuans.csv"
iiif_manifest = "https://ids.si.edu/ids/manifest/{}"

f = open("edan_iiif_results.csv", "w")
f.write("file_name,dams_uan,json_status_code,json_get_time,img_url,image_dl_time,img_status_code\n")
f.close()
        

with open(datafile, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # "file_name","dams_uan"
        try:
            print(row['file_name'], row['dams_uan'])
            # measure how long
            #  from https://stackoverflow.com/a/71357036/395223
            START_TIME = unix()
            r = requests.get(iiif_manifest.format(row['dams_uan']))
            json_get_time = unix() - START_TIME
            json_status_code = r.status_code
            data_json = json.loads(r.text)
            img_url = data_json['sequences'][0]['canvases'][0]['images'][0]['resource']['@id']
            START_TIME = unix()
            r = requests.get(img_url)
            image_dl_time = unix() - START_TIME
            img_status_code = r.status_code
            f = open("edan_iiif_results.csv", "a")
            f.write("{},{},{},{},{},{},{}\n".format(row['file_name'], row['dams_uan'], json_status_code, json_get_time, img_url, image_dl_time, img_status_code))
            f.close()
            print("{},{},{},{},{},{},{}\n".format(row['file_name'], row['dams_uan'], json_status_code, json_get_time, img_url, image_dl_time, img_status_code))
        except:
            continue

