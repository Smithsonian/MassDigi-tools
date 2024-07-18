#!/usr/bin/env python3
#
# Write IDs to Getty's ID Manager
#  Get receipts to confirm all records exist as intended
# 
# Ver 2024-06-24

import json
import requests
import settings
import csv
import sys
# from multiprocessing import Pool, cpu_count
import numpy as np
import re
import urllib.parse

import logging
import time
from time import strftime
from time import localtime
from time import time as unix 
from time import sleep

# MySQL
import pymysql

# Logging
current_time = strftime("%Y%m%d_%H%M%S", localtime())

logfile = 'logs/idmanager_{}.log'.format(current_time)
logging.basicConfig(filename=logfile, filemode='a', level=logging.DEBUG,
                    format='%(levelname)s | %(asctime)s | %(filename)s:%(lineno)s | %(message)s',
                    datefmt='%y-%b-%d %H:%M:%S')
logger = logging.getLogger("idmanager")

logger.info("Starting script on {}".format(current_time))


if len(sys.argv) != 2:
    # Missing arg?
    logger.error("Missing folder name")
    sys.exit(1)

# Get how long it takes to run
START_TIME = time.time()


# Get folder ID or folder name
try:
    folder_id = int(sys.argv[1])
    project_folder = None
except ValueError as e:
    folder_id = None
    project_folder = int(sys.argv[1])
    

NUM_CORES = settings.no_cores


# Generators
# Aspace generator
aspace_generator = "https://data.getty.edu/local/thesaurus/generators/aspace"
# Arches generator:
arches_generator = "https://data.getty.edu/local/thesaurus/generators/arches"
# DAMS generator:
dams_generator = "https://data.getty.edu/local/thesaurus/generators/dams"

# Motivations
motivation_arches_record = "https://data.getty.edu/local/thesaurus/motivations/arches_record"
motivation_part_of = "https://data.getty.edu/local/thesaurus/motivations/part_of"


# Login to ID Manager
params = {
        "username": settings.id_manager_username,
        "password": settings.id_manager_password
          }

r = requests.post("{}/auth".format(settings.id_manager_url), json=params)
response_json = json.loads(r.content.decode('utf-8'))
access_token = response_json['access_token']
Headers = {"Authorization": "Bearer {}".format(access_token)}


# Osprey Database
try:
    conn = pymysql.connect(host=settings.host,
                           user=settings.user,
                           passwd=settings.password,
                           database=settings.database,
                           port=settings.port,
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor,
                           autocommit=True)
    cur = conn.cursor()
except pymysql.Error as e:
    logger.error("Error connecting to the db: {}".format(e))
    sys.exit("Error connecting to the db: {}".format(e))


logger.info("Connected to db")

# Get folder from JPCA
#   only if QC Passed and it has been delivered to DAMS
if folder_id is None:
    query = "SELECT f.* FROM folders fol, qc_folders q WHERE fol.project_id = 201 and fol.project_folder = %(project_folder)s AND fol.folder_id = q.folder_id AND q.qc_status = 0 AND fol.delivered_to_dams = 0"
    cur.execute(query, {'project_folder': project_folder})
else:
    query = "SELECT * FROM folders WHERE project_id = 201 and folder_id = %(folder_id)s"
    cur.execute(query, {'folder_id': folder_id})

folder_info = cur.fetchall()
if len(folder_info) == 0:
    logger.error("Folder not found or not ready: {} {}".format(folder_id, project_folder))
    sys.exit("Folder not found or not ready: {} {}".format(folder_id, project_folder))
else:
    folder_info = folder_info[0]

# Get RefIDs from folder
get_refids = """SELECT 
                    distinct SUBSTRING_INDEX(f.file_name, '_', 1) as refid 
                FROM 
                    files f, 
                    folders fol
                WHERE 
                    f.folder_id = fol.folder_id AND
                    f.folder_id = %(folder_id)s"""
cur.execute(get_refids, {'folder_id': folder_info['folder_id']})
list_refids = cur.fetchall()
logger.info("list_refids: {}".format(len(list_refids)))

# cur.close()
# conn.close()


# Group ID
group_id = "dpo-jpca-fol{}".format(folder_info['folder_id'])


# Remove parallel to simplify
#def sendids(refid_row):
for refid_row in list_refids:
    refid = refid_row['refid']
    # Set group id for each batch using folder_id
    # group_id = "dpo-jpca-fol{}".format(folder_info['folder_id'])
    logger.info("refid: {}".format(refid))
    logger.info("group_id: {}".format(group_id))
    print("RefID: {} ({})".format(refid, group_id))    
    # try:
    #     conn = pymysql.connect(host=settings.host,
    #                         user=settings.user,
    #                         passwd=settings.password,
    #                         database=settings.database,
    #                         port=settings.port,
    #                         charset='utf8mb4',
    #                         cursorclass=pymysql.cursors.DictCursor,
    #                         autocommit=True)
    #     cur = conn.cursor()
    # except pymysql.Error as e:
    #     print(e)
    #     logger.error("Error connecting to the db: {}".format(e))
    #     sys.exit('System error')
    # 
    data_query = """
                with data1 as (select id1_value as refid, id2_value as hmo from jpc_massdigi_ids jmi where 
                    id_relationship  = 'refid_hmo' and id1_value = %(refid)s),
                    
                    data2 as (select id1_value as hmo, id2_value as tif from jpc_massdigi_ids jmi where 
                    id_relationship  = 'hmo_tif'),
                    
                    data3 as (select id1_value as tif, id2_value as dams from jpc_massdigi_ids jmi where 
                    id_relationship  = 'tif_dams')
                    
                select data1.refid, data1.hmo, data2.tif, data3.dams
                from data1, data2, data3 
                where data1.hmo=data2.hmo and data2.tif=data3.tif"""
    cur.execute(data_query, {'refid': refid})
    data_vals = cur.fetchall()
    if len(data_vals) == 0:
        logger.error("HMO data missing for folder {}".format(folder_id))
        print("HMO data missing for folder {}".format(folder_id))
        sys.exit(0)
    #
    for row in data_vals:
        logger.info("DAMS UAN: {}".format(row['dams']))
        # "refid","hmo","tif","dams"
        dams_uan = "urn:dams:{}".format(row['dams'])
        # tif_iiif_manifest = data_row[6]
        arches_record = "https://arches.jpcarchive.org/resources/{}".format(row['hmo'])
        aspace_refid = "urn:aspace:{}".format(row['refid'])
        logger.info("dams_uan, arches_record, aspace_refid: {}".format(dams_uan, arches_record, aspace_refid))
        # DAMS to ASpace
        params = {
                        "group_id": group_id,
                        "body": {"id": dams_uan, "generator": dams_generator},
                        "target": {"id": aspace_refid, "generator": aspace_generator},
                        "motivation": motivation_part_of
                        }
        try:
            r = requests.post("{}/links".format(settings.id_manager_url), json=params, headers=Headers)
            if r.status_code != 201:
                if r.status_code == 200:
                    url_to_check = "{}/links?body_id={}&target_id={}".format(settings.id_manager_url, urllib.parse.quote_plus(dams_uan), urllib.parse.quote_plus(aspace_refid))
                    r = requests.get(url_to_check)
                    results = json.loads(r.text)
                    results_id = results['first']['items'][0]['id']
                else:
                    logger.error("INSERT FAILED - DAMS-ASPACE Link")
                    logger.error("dams_uan, arches_record, aspace_refid: {}".format(dams_uan, arches_record, aspace_refid))
                    continue
            else:
                results = json.loads(r.text)
                results_id = results['id']
            r = requests.get(results_id)
            print(r.status_code)
            res_check = json.loads(r.text)
            if r.status_code == 200 and res_check['body']['id'] == dams_uan and res_check['target']['id'] == aspace_refid:
                post_proc = "INSERT INTO file_postprocessing (file_id, post_step, post_results, post_info) (SELECT file_id, %(post_step)s, 0, %(post_info)s FROM files WHERE folder_id = %(folder_id)s and file_name like %(ref_id)s) ON DUPLICATE KEY UPDATE post_results = 0, post_info = %(post_info)s"
                logger.info(post_proc)
                cur.execute(post_proc, {'folder_id': folder_info['folder_id'], 'post_step': 'id_manager_aspace', 'post_info': results_id, 'ref_id': "{}_%".format(refid)})
            else:
                post_proc = "INSERT INTO file_postprocessing (file_id, post_step, post_results, post_info) (SELECT file_id, %(post_step)s, 1, %(post_info)s FROM files WHERE folder_id = %(folder_id)s and file_name like %(ref_id)s) ON DUPLICATE KEY UPDATE post_results = 1, post_info = %(post_info)s"
                logger.info(post_proc)
                cur.execute(post_proc, {'folder_id': folder_info['folder_id'], 'post_step': 'id_manager_aspace', 'post_info': "Link not found: {}".format(results_id), 'ref_id': "{}_%".format(refid)})
        except:
            post_proc = "INSERT INTO file_postprocessing (file_id, post_step, post_results, post_info) (SELECT file_id, %(post_step)s, 1, %(post_info)s FROM files WHERE folder_id = %(folder_id)s and file_name like %(ref_id)s) ON DUPLICATE KEY UPDATE post_results = 1, post_info = %(post_info)s"
            logger.info(post_proc)
            cur.execute(post_proc, {'folder_id': folder_info['folder_id'], 'post_step': 'id_manager_aspace', 'post_info': "ID Manager id_manager_aspace failed: {}, {}, {}".format(group_id, dams_uan, aspace_refid), 'ref_id': "{}_%".format(refid)})
        # DAMS to Arches
        try:
            params = {
                        "group_id": group_id,
                        "body": {"id": dams_uan, "generator": dams_generator},
                        "target": {"id": arches_record, "generator": arches_generator},
                        "motivation": motivation_arches_record
                        }
            r = requests.post("{}/links".format(settings.id_manager_url), json=params, headers=Headers)
            if r.status_code != 201:
                if r.status_code == 200:
                    url_to_check = "{}/links?body_id={}&target_id={}".format(settings.id_manager_url, urllib.parse.quote_plus(dams_uan), urllib.parse.quote_plus(arches_record))
                    r = requests.get(url_to_check)
                    results = json.loads(r.text)
                    results_id = results['first']['items'][0]['id']
                else:
                    logger.error("INSERT FAILED - DAMS-ARCHES Link")
                    logger.error("dams_uan, arches_record, aspace_refid: {}".format(dams_uan, arches_record, aspace_refid))
                    continue
            else:
                results = json.loads(r.text)
                results_id = results['id']
            results = json.loads(r.text)
            results_id = results['id']
            r = requests.get(results_id)
            print(r.status_code)
            if r.status_code == 200:
                post_proc = "INSERT INTO file_postprocessing (file_id, post_step, post_results, post_info) (SELECT file_id, %(post_step)s, 0, %(post_info)s FROM files WHERE folder_id = %(folder_id)s and file_name like %(ref_id)s) ON DUPLICATE KEY UPDATE post_results = 0, post_info = %(post_info)s".format(row['refid'])
                logger.info(post_proc)
                cur.execute(post_proc, {'folder_id': folder_info['folder_id'], 'post_step': 'id_manager_arches', 'post_info': results_id, 'ref_id': "{}_%".format(row['refid'])})
            else:
                post_proc = "INSERT INTO file_postprocessing (file_id, post_step, post_results, post_info) (SELECT file_id, %(post_step)s, 1, %(post_info)s FROM files WHERE folder_id = %(folder_id)s and file_name like %(ref_id)s) ON DUPLICATE KEY UPDATE post_results = 1, post_info = %(post_info)s".format(row['refid'])
                logger.info(post_proc)
                cur.execute(post_proc, {'folder_id': folder_info['folder_id'], 'post_step': 'id_manager_arches', 'post_info': "Link not found: {}".format(results_id), 'ref_id': "{}_%".format(row['refid'])})
        except:
            post_proc = "INSERT INTO file_postprocessing (file_id, post_step, post_results, post_info) (SELECT file_id, %(post_step)s, 1, %(post_info)s FROM files WHERE folder_id = %(folder_id)s and file_name like %(ref_id)s) ON DUPLICATE KEY UPDATE post_results = 1, post_info = %(post_info)s"
            logger.info(post_proc)
            cur.execute(post_proc, {'folder_id': folder_info['folder_id'], 'post_step': 'id_manager_arches', 'post_info': "ID Manager id_manager_arches failed: {}, {}, {}".format(group_id, dams_uan, arches_record), 'ref_id': "{}_%".format(refid)})
    # cur.close()
    # conn.close()
    # return


# process each refid in parallel
# pool = Pool(NUM_CORES)
# results = pool.map(sendids, list_refids)


######################################
# Check ID Manager and get receipts
######################################

dams_uan_prefix = "urn:dams:"
aspace_prefix = "urn:aspace:"
arches_prefix = "https://arches.jpcarchive.org/resources/"

# Queries
fileid_query = "SELECT file_id FROM files WHERE dams_uan = %(dams_uan)s"
insert_post_proc = "INSERT INTO file_postprocessing (file_id, post_step, post_results, post_info) VALUES (%(file_id)s, %(post_step)s, 0, %(post_info)s) ON DUPLICATE KEY UPDATE post_results = 0, post_info = %(post_info)s"

# Work group with pagination
for j in range(1, 1000):
    group_url = "{}/groups/{}/page/{}".format(settings.id_manager_url, group_id, j)
    logger.info(group_url)
    r = requests.get(group_url)
    if r.status_code == 404:
        logger.info("Found 404: {}".format(group_url))
        break
    else:
        group_data = json.loads(r.text)
        group_items = group_data['items']
        for item in group_items:
            item_id = item['id']
            logger.info("item_id: {}".format(item_id))
            target = item['target']
            body = item['body']
            dams_uan = body['id'].replace(dams_uan_prefix, "")
            logger.info("dams_uan: {}".format(dams_uan))
            if target['generator'] == aspace_generator:
                # Aspace item
                post_step = "id_manager_aspace"
            elif target['generator'] == arches_generator:
                # Arches item
                post_step = "id_manager_arches"
            # Get the file_id
            cur.execute(fileid_query, {'dams_uan': dams_uan})
            file_id = cur.fetchall()
            logger.info("file_id query: {}".format(file_id))
            if len(file_id) == 0:
                logger.error("file_id query didn't find a match: {} (dams_uan: {})".format(file_id, dams_uan))
                continue
            file_id = file_id[0]['file_id']
            # Save the post_processing
            cur.execute(insert_post_proc, {'file_id': file_id, 'post_step': post_step, 'post_info': item_id})


# Anything missing?
# id_manager_aspace
post_step = "id_manager_aspace"
cur.execute("SELECT f.* from files f WHERE f.folder_id = %(folder_id)s and f.file_id NOT IN (SELECT file_id from file_postprocessing WHERE post_step = %(post_step)s)", {'folder_id': folder_id, 'post_step': post_step})
missing_files = cur.fetchall()
if len(missing_files) > 0:
    cur.execute("INSERT INTO folders_badges (folder_id, badge_type, badge_css, badge_text) VALUES (%(folder_id)s, %(post_step)s, 'bg-danger', 'ID Manager-ASpace Error')", {'folder_id': folder_id, 'post_step': post_step})
    for mfile in missing_files:
        cur.execute("INSERT INTO file_postprocessing (file_id, post_step, post_results, post_info) VALUES (%(file_id)s, %(post_step)s, 1, 'ID Manager Failed') ON DUPLICATE KEY UPDATE post_results = 1, post_info = 'ID Manager Failed'", {'file_id': mfile['file_id'], 'post_step': post_step})



# id_manager_arches
post_step = "id_manager_arches"
cur.execute("SELECT f.* from files f WHERE f.folder_id = %(folder_id)s and f.file_id NOT IN (SELECT file_id from file_postprocessing WHERE post_step = %(post_step)s)", {'folder_id': folder_id, 'post_step': post_step})
missing_files = cur.fetchall()
if len(missing_files) > 0:
    cur.execute("INSERT INTO folders_badges (folder_id, badge_type, badge_css, badge_text) VALUES (%(folder_id)s, %(post_step)s, 'bg-danger', 'ID Manager-Arches Error')", {'folder_id': folder_id, 'post_step': post_step})
    for mfile in missing_files:
        cur.execute("INSERT INTO file_postprocessing (file_id, post_step, post_results, post_info) VALUES (%(file_id)s, %(post_step)s, 1, 'ID Manager Failed') ON DUPLICATE KEY UPDATE post_results = 1, post_info = 'ID Manager Failed'", {'file_id': mfile['file_id'], 'post_step': post_step})



# Close DB
cur.close()
conn.close()

END_TIME = time.time()
TOTAL_TIME = "{} sec".format((END_TIME - START_TIME))

# print the difference between start 
# and end time in secs
print("\n\n Execution time was: {} secs\n\n".format(TOTAL_TIME))

logger.info("Ending script on {}".format(strftime("%Y%m%d_%H%M%S", localtime())))

logger.info("Script took: {} secs".format(TOTAL_TIME))

sys.exit(0)
