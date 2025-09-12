#!/usr/bin/env python3
# 
# Create stub records in Arches
# Script adapted from Getty-provided ingest script
#
# Ver 2025-03-10
#
import requests
from typing import Final
from pydantic import BaseModel
# from typing import Tuple
import json
import uuid
import sys
import os
import logging
from time import strftime
from time import localtime

import archesapiclient

# MySQL
import pymysql

import settings



# Logging
current_time = strftime("%Y%m%d_%H%M%S", localtime())

logfile = 'logs/arches_{}.log'.format(current_time)
logging.basicConfig(filename=logfile, filemode='a', level=logging.DEBUG,
                    format='%(levelname)s | %(asctime)s | %(filename)s:%(lineno)s | %(message)s',
                    datefmt='%y-%b-%d %H:%M:%S')
logger = logging.getLogger("arches")

logger.info("Starting script on {}".format(current_time))



if len(sys.argv) != 2:
    # Missing arg?
    logger.error("Missing folder name")
    sys.exit(1)

# Get folder ID or folder name
try:
    folder_id = int(sys.argv[1])
    project_folder = None
except ValueError as e:
    folder_id = None
    project_folder = int(sys.argv[1])


"""
The Graph in arches is as explained here https://arches.readthedocs.io/en/7.2/data-model/?highlight=graph#graph-definition
a data model respenting top level objects like Visual Works, Physical Objects etc.
The id is autocreated from arches when creating the model and doesn't change, unless the Model represented by this graph,
gets deleted and re-created.
"""

GRAPH_ID: Final[str] = settings.graph_id
ARCHES_ENDPOINT: str = settings.arches_api

RESOURCES_ENDPOINT: Final[str] = f"{ARCHES_ENDPOINT}/resources"
RESOURCE_URL: Final[str] = f"{ARCHES_ENDPOINT}/resource"



url = ARCHES_ENDPOINT
client_id = settings.arches_api_clientid
username = settings.arches_api_username
password = settings.arches_api_password

a_client = archesapiclient.ArchesClient(url, client_id, username, password)



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

logger.info("Connected to db")



query = "SELECT * FROM folders WHERE project_id = 220 and project_folder = %(project_folder)s"
cur.execute(query, {'project_folder': project_folder})



# Get folder from JPCA
#   only if QC Passed and it has been delivered to DAMS
if folder_id is None:
    query = "SELECT * FROM folders WHERE project_id = 220 and project_folder = %(project_folder)s"
    cur.execute(query, {'project_folder': project_folder})
else:
    query = "SELECT * FROM folders WHERE project_id = 220 and folder_id = %(folder_id)s"
    cur.execute(query, {'folder_id': folder_id})


folder_info = cur.fetchall()

if len(folder_info) == 0:
    logger.error("Folder not found: {} {}".format(folder_id, project_folder))
    sys.exit("Folder not found: {} {}".format(folder_id, project_folder))


folder_info = folder_info[0]

get_refids = """SELECT 
                    distinct SUBSTRING_INDEX(f.file_name, '_', 1) as refid 
                FROM 
                    files f, 
                    qc_folders q,
                    folders fol
                WHERE 
                    f.folder_id = q.folder_id AND 
                    q.qc_status = 0 AND 
                    f.folder_id = fol.folder_id AND
                    fol.delivered_to_dams = 0 AND 
                    f.folder_id = %(folder_id)s"""
cur.execute(get_refids, {'folder_id': folder_info['folder_id']})
list_refids = cur.fetchall()
logger.info("list_refids: {}".format(len(list_refids)))


for refid in list_refids:
    refid = refid['refid']
    logger.info("refid: {}".format(refid))

    query = ("""
        with data as (
                SELECT id1_value as refid, id2_value as hmo FROM dpo_osprey.jpc_massdigi_ids 
                        where id_relationship = 'refid_hmo' and id1_value= %(refid)s
                        ),
        data2 as (select 
                        id1_value as hmo, 
                        SUBSTRING_INDEX(SUBSTRING_INDEX(id2_value , '_', -2), '_', 1) as item,
                        f.project_folder 
                        FROM jpc_massdigi_ids j, folders f 
                        where j.id_relationship = 'hmo_tif' and j.folder_id = %(folder_id)s and
                                j.folder_id = f.folder_id 
                        group by hmo, item)
        select d.*, 
            concat(j.unit_title, ' - Box ', 
                            replace(SUBSTRING_INDEX(SUBSTRING_INDEX(d2.project_folder , '_2024', 1), '_', -2), '_', '-')
                            , 
                            ' Folder ', j.archive_folder, ' Item ', 
                    d2.item
                            ) as unit_title, 
            j.archive_box, d2.project_folder, d2.item
            from data d, data2 d2, jpc_aspace_data j where d.refid=j.refid
            and d.hmo=d2.hmo
        """)

    cur.execute(query, {'refid': refid, 'folder_id': folder_id})
    data = cur.fetchall()
    logger.info("Got {} records".format(len(data)))

    for row in data:
        # Get HMO ID from database
        hmo_id = row['hmo']
        logger.info("Working on HMO: {}".format(hmo_id))

        # Convert id
        id = "https://arches.jpcarchive.org/{}".format(hmo_id)

        # # TO EXPAND
        # Get title, box, and folder of HMO from folder title in database
        # Example:
        #   title = "3T"
        #   box_no = "BI-001A"
        #   folder_no = "001"
        title = row['unit_title']
        # folder_no = row['archive_folder']
        # box_no = row['archive_box']
        sequence = int(title[-4:])
        refid = row['refid']

        # Read data model from file
        f = open('jpc_data_model_20231218.json')
        json_data_model = json.load(f)
        f.close()

        # Replace values in json
        json_data_model['id'] = f"https://arches.jpcarchive.org/object/{hmo_id}"
        json_data_model['_label'] = title
        json_data_model['identified_by'][0]['content'] = title
        json_data_model['identified_by'][0]['id'] = "https://arches.jpcarchive.org/object/{}/name/1".format(hmo_id)
        json_data_model['assigned_by'][0]['id'] = "https://arches.jpcarchive.org/object/{}/sequence-assignment".format(hmo_id)
        json_data_model['assigned_by'][0]['assigned'][0]['id'] = "https://arches.jpcarchive.org/object/{}/sequence-position".format(hmo_id)
        json_data_model['assigned_by'][0]['assigned'][0]['value'] = sequence
        json_data_model['assigned_by'][0]['used_specific_object'][0]['_label'] = "Item order for urn:aspace:{}".format(refid)
        json_data_model['assigned_by'][0]['used_specific_object'][0]['refers_to'][0]['identified_by'][0]['content'] = refid

        record_id = a_client.put_record(graph_id=GRAPH_ID, data=json_data_model, rec_id=hmo_id)

        logger.info("HMO {} saved".format(hmo_id))
        # print(hmo_id)
        
        # Get the record back to confirm it exists
        record = a_client.get_record(hmo_id)

        post_step = 'arches_record'
        if hmo_id in record['id']:
            post_proc = "INSERT INTO file_postprocessing (file_id, post_step, post_results, post_info) (SELECT file_id, %(post_step)s, 0, concat('https://dev-arches.jpcarchive.org/report/', %(hmo_id)s) FROM files f WHERE SUBSTRING_INDEX(f.file_name, '_', 2) = concat(%(refid)s, '_', %(item)s)) ON DUPLICATE KEY UPDATE post_results = 0, post_info = concat('https://dev-arches.jpcarchive.org/report/', %(hmo_id)s)"
            cur.execute(post_proc, {'folder_id': folder_info['folder_id'], 'post_step': post_step, 'hmo_id': hmo_id, 'refid': refid, 'item': row['item']})
        else:
            post_proc = "INSERT INTO file_postprocessing (file_id, post_step, post_results, post_info) (SELECT file_id, %(post_step)s, 1, concat('Arches record not found: https://dev-arches.jpcarchive.org/report/', %(hmo_id)s) FROM files f WHERE SUBSTRING_INDEX(f.file_name, '_', 2) = concat(%(refid)s, '_', %(item)s)) ON DUPLICATE KEY UPDATE post_results = 1, post_info = concat('Arches record not found: https://dev-arches.jpcarchive.org/report/', %(hmo_id)s)"
            cur.execute(post_proc, {'folder_id': folder_info['folder_id'], 'post_step': post_step, 'hmo_id': hmo_id, 'refid': refid, 'item': row['item']})
            cur.execute("INSERT INTO folders_badges (folder_id, badge_type, badge_css, badge_text) VALUES (%(folder_id)s, %(post_step)s, 'bg-danger', 'Arches Error')", {'folder_id': folder_info['folder_id'], 'post_step': post_step})





current_time = strftime("%Y%m%d_%H%M%S", localtime())
logger.info("Script finished on {}".format(current_time))

cur.close()
conn.close()
