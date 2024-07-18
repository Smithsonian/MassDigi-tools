#!/usr/bin/env python3
#
# Grab all ids from Arches and update Osprey
#  to make sure data isn't being lost somewhere
# 
# Ver 2024-06-25

# import json
# import requests
import settings
import sys
from multiprocessing import Pool
# import urllib.parse
import os
import archesapiclient

import logging
import time
from time import strftime
from time import localtime
from time import time as unix 
from time import sleep

# MySQL
import pymysql


# CLI args
q_limit = sys.argv[1]
q_offset = sys.argv[2]


# Logging
current_time = strftime("%Y%m%d_%H%M%S", localtime())

if not os.path.exists('logs'):
    os.makedirs('logs')

logfile = 'logs/arches_{}_{}.log'.format(current_time, q_offset)
logging.basicConfig(filename=logfile, filemode='a', level=logging.DEBUG,
                    format='%(levelname)s | %(asctime)s | %(filename)s:%(lineno)s | %(message)s',
                    datefmt='%y-%b-%d %H:%M:%S')
logger = logging.getLogger("arches")

logger.info("Starting script on {}".format(current_time))


# Get how long it takes to run
START_TIME = time.time()

# NUM_CORES = settings.no_cores


ARCHES_ENDPOINT: str = settings.arches_api
url = ARCHES_ENDPOINT
client_id = settings.arches_api_clientid
username = settings.arches_api_username
password = settings.arches_api_password

a_client = archesapiclient.ArchesClient(url, client_id, username, password)


# Empty id_manager post steps
try:
    conn = pymysql.connect(host=settings.host,
                        user=settings.user,
                        passwd=settings.password,
                        database=settings.database,
                        port=settings.port,
                        charset='utf8mb4',
                        cursorclass=pymysql.cursors.DictCursor,
                        autocommit=True)
    conn.time_zone = '-04:00'
    cur = conn.cursor()
except pymysql.Error as e:
    print(e)
    logger.error("Error connecting to the db: {}".format(e))
    sys.exit('System error')


if q_offset == "0":
    cur.execute("DELETE FROM file_postprocessing WHERE post_step = 'arches_record' and file_id in (select file_id from files where folder_id in (select folder_id from folders where project_id = 186 or project_id = 201))")


query = "SELECT distinct id1_value as hmo_id FROM jpc_massdigi_ids WHERE id_relationship = 'hmo_tif' ORDER BY id1_value LIMIT {} OFFSET {}"
cur.execute(query.format(q_limit, q_offset))
hmo_data = cur.fetchall()


# cur.close()
# conn.close()

post_step = 'arches_record'
get_files_query = "SELECT f.file_id from files f, jpc_massdigi_ids j WHERE f.file_name = j.id2_value AND j.id1_value = %(hmo_id)s AND j.id_relationship = 'hmo_tif'"


#def process_hmo(row):
for row in hmo_data:
    hmo_id = row['hmo_id']
    logger.info("hmo_id: {}".format(hmo_id))
    # # Database
    # try:
    #     conn = pymysql.connect(host=settings.host,
    #                         user=settings.user,
    #                         passwd=settings.password,
    #                         database=settings.database,
    #                         port=settings.port,
    #                         charset='utf8mb4',
    #                         cursorclass=pymysql.cursors.DictCursor,
    #                         autocommit=True)
    #     conn.time_zone = '-04:00'
    #     cur = conn.cursor()
    # except pymysql.Error as e:
    #     print(e)
    #     logger.error("Error connecting to the db: {}".format(e))
    #     sys.exit('System error')
    # logger.info("Connected to db")
    # Get file_id's for this hmo    
    cur.execute(get_files_query, {'hmo_id': hmo_id})
    files = cur.fetchall()    
    # Check for the HMO in Arches
    try:
        record = a_client.get_record(hmo_id)
        record_found = True
    except:
        record_found = False
        logger.error("Arches query failed: {}".format(hmo_id))
    for file in files:
        if record_found is False:
            post_proc = "INSERT INTO file_postprocessing (file_id, post_step, post_results, post_info) VALUES (%(file_id)s, %(post_step)s, 1, 'Arches HMO not found' ) ON DUPLICATE KEY UPDATE post_results = 1, post_info = 'Arches HMO not found'"
            cur.execute(post_proc, {'file_id': file['file_id'], 'post_step': post_step})
            logger.error("Arches record not found: {}||file_id:{}".format(hmo_id, file['file_id']))
        if hmo_id in record['id']:
            post_proc = "INSERT INTO file_postprocessing (file_id, post_step, post_results, post_info) VALUES (%(file_id)s, %(post_step)s, 0, concat('https://dev-arches.jpcarchive.org/report/', %(hmo_id)s) ) ON DUPLICATE KEY UPDATE post_results = 1, post_info = concat('https://dev-arches.jpcarchive.org/report/', %(hmo_id)s)"
            cur.execute(post_proc, {'file_id': file['file_id'], 'post_step': post_step, 'hmo_id': hmo_id})
            logger.info("Arches record found: {}|{}|file_id:{}".format(hmo_id, record['id'], file['file_id']))
        else:
            post_proc = "INSERT INTO file_postprocessing (file_id, post_step, post_results, post_info) VALUES (%(file_id)s, %(post_step)s, 1, 'Arches HMO not found' ) ON DUPLICATE KEY UPDATE post_results = 1, post_info = 'Arches HMO not found'"
            cur.execute(post_proc, {'file_id': file['file_id'], 'post_step': post_step})
            logger.error("Arches record not found: {}||file_id:{}".format(hmo_id, file['file_id']))

    # return True


# process each refid in parallel
# pool = Pool(NUM_CORES)
# results = pool.map(process_group, list_groups)

cur.close()
conn.close()

END_TIME = time.time()
TOTAL_TIME = "{} sec".format((END_TIME - START_TIME))

# print the difference between start 
# and end time in milli. secs
print("The time of execution of above program is :{}".format(TOTAL_TIME))

logger.info("Ending script on {}".format(strftime("%Y%m%d_%H%M%S", localtime())))
logger.info("Script took: {}".format(TOTAL_TIME))

sys.exit(0)
