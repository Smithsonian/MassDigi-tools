#!/usr/bin/env python3
#
# Check that the IIIF Manifests exist
# 

import requests
from requests.auth import HTTPBasicAuth
import json
import requests
import logging
from time import time as unix 
from time import strftime
from time import localtime
import sys

# Parallel
import multiprocessing
from multiprocessing import Pool

# MySQL
import pymysql
import settings


iiif_manifest_template = "https://iiif.jpcarchive.org/iiif/v2.0/manifest/arches:{}"


# Logging
current_time = strftime("%Y%m%d_%H%M%S", localtime())

logfile = 'logs/iiif_{}.log'.format(current_time)
logging.basicConfig(filename=logfile, filemode='a', level=logging.DEBUG,
                    format='%(levelname)s | %(asctime)s | %(filename)s:%(lineno)s | %(message)s',
                    datefmt='%y-%b-%d %H:%M:%S')
logger = logging.getLogger("iiif")

logger.info("Starting script on {}".format(current_time))


# # Connect to db
try:
    conn = pymysql.connect(host=settings.host,
                           user=settings.user,
                           password=settings.password,
                           database=settings.database,
                           port=settings.port,
                           charset='utf8mb4',
                           autocommit=True,
                           cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()
except pymysql.Error as e:
    print(e)
    sys.exit(1)

logger.info("Connected to db")



query = "SELECT distinct id1_value as hmoid FROM jpc_massdigi_ids WHERE id_relationship = 'hmo_tif'"
cur.execute(query)
hmos = cur.fetchall()



cur.close()
conn.close()



#for hmo in hmos:
def check_hmo(hmo):



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





with Pool(settings.no_cores) as pool:
    pool.map(check_hmo, hmos)
    pool.close()
    pool.join()



# cur.close()
# conn.close()


current_time = strftime("%Y%m%d_%H%M%S", localtime())
logger.info("Script finished on {}".format(current_time))



