#!/usr/bin/env python3
# 
# Check if record exists in RCV
#
# Ver 2024-07-22
#

import requests
from requests.auth import HTTPBasicAuth
import json
import sys
import logging
from time import strftime
from time import localtime

# Parallel
import multiprocessing
from multiprocessing import Pool

# MySQL
import pymysql

import settings



# Logging
current_time = strftime("%Y%m%d_%H%M%S", localtime())

logfile = 'logs/rcv_{}.log'.format(current_time)
logging.basicConfig(filename=logfile, filemode='a', level=logging.DEBUG,
                    format='%(levelname)s | %(asctime)s | %(filename)s:%(lineno)s | %(message)s',
                    datefmt='%y-%b-%d %H:%M:%S')
logger = logging.getLogger("rcv")

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


query = "DELETE FROM file_postprocessing WHERE post_step = 'rcv_record' and post_results = 9"
cur.execute(query)

cur.close()
conn.close()

insert_query = "INSERT INTO file_postprocessing (file_id, post_step, post_results, post_info) (SELECT file_id, 'rcv_record', %(hmo_res)s, %(hmo_info)s FROM files f, jpc_massdigi_ids j WHERE f.file_name = j.id2_value AND j.id1_value = %(hmoid)s and j.id_relationship = 'hmo_tif' and f.folder_id in (select folder_id from folders where (project_id = 186 or project_id = 201))) ON DUPLICATE KEY UPDATE post_results = 1, post_info = %(hmo_info)s"



#for hmo in hmos:
def check_hmo(hmo):
    hmoid = hmo['hmoid']

    # Connect to db
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

    logger.info("hmoid: {}".format(hmoid))

    basic = HTTPBasicAuth(settings.rcv_login, settings.rcv_pass)
    r = requests.get(settings.rcv_url.format(hmoid), auth=basic)

    if r.status_code == 200:
        hmo_data = json.loads(r.text)
        if hmo_data['id'] == settings.rcv_url.format(hmoid):
            logger.info("Found the HMO: {}".format(hmoid))
            hmo_res = 0
            hmo_info = settings.rcv_url.format(hmoid)
            cur.execute(insert_query, {'hmoid': hmoid, 'hmo_res': hmo_res, 'hmo_info': hmo_info})
        else:
            logger.info("Got an unexpected answer from the server: {} != {}".format(hmo_data['id'], settings.rcv_url.format(hmoid)))
            sys.exit(1)
    elif r.status_code == 404:
        hmo_data = json.loads(r.text)
        logger.info("Did NOT find the HMO: {}".format(hmoid))
        hmo_res = 9
        hmo_info = "Record not found"
        cur.execute(insert_query, {'hmoid': hmoid, 'hmo_res': hmo_res, 'hmo_info': hmo_info})
    else:
        logger.info("Got an error from the server: {}".format(r.status_code))
        sys.exit(1)
    # 
    cur.close()
    conn.close()
    print("hmoid: {}".format(hmoid))
    return



with Pool(settings.no_cores) as pool:
    pool.map(check_hmo, hmos)
    pool.close()
    pool.join()



# cur.close()
# conn.close()


current_time = strftime("%Y%m%d_%H%M%S", localtime())
logger.info("Script finished on {}".format(current_time))

