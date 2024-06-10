#!/usr/bin/env python3
#
# Write IDs to Getty's ID Manager

# Ver 2024-05-02

import json
import requests
import settings
import csv
import sys

import logging
from time import strftime
from time import localtime

# MySQL
import pymysql

# Logging
current_time = strftime("%Y%m%d_%H%M%S", localtime())

logfile = 'idmanager_{}.log'.format(current_time)
logging.basicConfig(filename=logfile, filemode='a', level=logging.DEBUG,
                    format='%(levelname)s | %(asctime)s | %(filename)s:%(lineno)s | %(message)s',
                    datefmt='%y-%b-%d %H:%M:%S')
logger = logging.getLogger("idmanager")

logger.info("Starting script on {}".format(current_time))


if len(sys.argv) != 2:
    # Missing arg?
    logger.error("Missing folder name")
    sys.exit(1)


project_folder = sys.argv[1]


params = {
        "username": settings.id_manager_username,
        "password": settings.id_manager_password
          }

r = requests.post("{}/id-management/auth".format(settings.id_manager_url), json=params)

response_json = json.loads(r.content.decode('utf-8'))

access_token = response_json['access_token']

Headers = {"Authorization": "Bearer {}".format(access_token)}



# To add the link between the database with the IDs and which ones are going to be written in ID Manager
#   Loop each ID associated with an image or an HMO?
#   Trigger once the DAMS UAN is stored.

# Format of the post body for ID Manager
# params = {
#         "body": {"id": "MANIFEST URI", "generator": "WHAT GOES HERE IS A GOOD QUESTION, SEE BELOW"},
#         "target": {"id": "URI OF THE THING/IMAGE/RECORD", "generator": "SIMILAR, GOOD QUESTION"},
#         "motivation": "https://data.getty.edu/local/thesaurus/motivations/iiif_manifest_of"
#         }
#
#

# Generators
# Osprey generator
osprey_generator = "https://data.getty.edu/local/thesaurus/generators/osprey"
# Aspace generator
aspace_generator = "https://data.getty.edu/local/thesaurus/generators/aspace"
# Arches generator:
arches_generator = "https://data.getty.edu/local/thesaurus/generators/arches"
# DAMS generator:
dams_generator = "https://data.getty.edu/local/thesaurus/generators/dams"
# EDAN generator:
edan_generator = "https://data.getty.edu/local/thesaurus/generators/edan"


# Motivations
#   - commented the ones we won't seem to need and variables are now "motivation_{shortname}"

# ASpace motivation
# aspace_motivation = "https://data.getty.edu/local/thesaurus/motivations/part_of"

# Slug - Links the body to a target slug number
#   Slug record in Arches for the HMO (to confirm)
# slug_motivation = "https://data.getty.edu/local/thesaurus/motivations/arches_record"
motivation_arches_record = "https://data.getty.edu/local/thesaurus/motivations/arches_record"

# # RefID - "The body object contains a 'RefId' identifier, represented here as the target id"
# #   "The associated body resource (as part of a Web Annotation) contains a RefID (target resource).
# #       The relationship is not specific enough for a more granular definition."
# refid_motivation = "https://data.getty.edu/local/thesaurus/motivations/contains-refid"

# IIIF manifest of images
# iiif_manifest_images_motivation = "https://data.getty.edu/local/thesaurus/motivations/iiif_manifest_of"

# IIIF manifest of HMO
# iiif_manifest_hmo_motivation = "https://data.getty.edu/local/thesaurus/motivations/iiif_hmo_manifest_of"

# hmo_image_motivation = "https://data.getty.edu/local/thesaurus/motivations/part_of"
motivation_part_of = "https://data.getty.edu/local/thesaurus/motivations/part_of"


# For testing and too easy delete
# group_id = "dpo-jpca-{}".format(strftime("%Y%m%d", localtime()))
group_id = "dpo-jpca-20240516"

logger.info("group_id: {}".format(group_id))
print("ID Manager GroupID: {}".format(group_id))

# Database
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
    print(e)
    logger.error("Error connecting to the db: {}".format(e))
    sys.exit('System error')


logger.info("Connected to db")

query = "SELECT * FROM folders WHERE project_id = 201 and project_folder = %(project_folder)s"
cur.execute(query, {'project_folder': project_folder})
folder_info = cur.fetchall()[0]



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
        r = requests.post("{}/id-management/links".format(settings.id_manager_url), json=params, headers=Headers)
        if r.status_code != 201:
            logger.error("INSERT FAILED - DAMS-ASPACE Link")
            sys.exit("INSERT FAILED - DAMS-ASPACE Link")
        results = json.loads(r.text)
        results_id = results['id']
        r = requests.get(results_id, headers=Headers)
        print(r.status_code)
        if r.status_code == 200:
            post_proc = "INSERT INTO file_postprocessing (file_id, post_step, post_results, post_info) (SELECT file_id, %(post_step)s, 0, %(post_info)s FROM files WHERE folder_id = %(folder_id)s and file_name like %(ref_id)s) ON DUPLICATE KEY UPDATE post_results = 0".format(row['refid'])
            logger.info(post_proc)
            cur.execute(post_proc, {'folder_id': folder_info['folder_id'], 'post_step': 'id_manager_aspace', 'post_info': results_id, 'ref_id': "{}_%".format(row['refid'])})
        else:
            post_proc = "INSERT INTO file_postprocessing (file_id, post_step, post_results, post_info) (SELECT file_id, %(post_step)s, 1, %(post_info)s FROM files WHERE folder_id = %(folder_id)s and file_name like %(ref_id)s) ON DUPLICATE KEY UPDATE post_results = 1".format(row['refid'])
            logger.info(post_proc)
            cur.execute(post_proc, {'folder_id': folder_info['folder_id'], 'post_step': 'id_manager_aspace', 'post_info': "Link not found: {}".format(results_id), 'ref_id': "{}_%".format(row['refid'])})
     
        # DAMS to Arches
        params = {
                        "group_id": group_id,
                        "body": {"id": dams_uan, "generator": dams_generator},
                        "target": {"id": arches_record, "generator": arches_generator},
                        "motivation": motivation_arches_record
                        }
        r = requests.post("{}/id-management/links".format(settings.id_manager_url), json=params, headers=Headers)
        if r.status_code != 201:
            logger.error("INSERT FAILED - DAMS-ARCHES Link")
            sys.exit("INSERT FAILED - DAMS-ARCHES Link")
        results = json.loads(r.text)
        results_id = results['id']
        r = requests.get(results_id, headers=Headers)
        print(r.status_code)
        if r.status_code == 200:
            post_proc = "INSERT INTO file_postprocessing (file_id, post_step, post_results, post_info) (SELECT file_id, %(post_step)s, 0, %(post_info)s FROM files WHERE folder_id = %(folder_id)s and file_name like %(ref_id)s) ON DUPLICATE KEY UPDATE post_results = 0".format(row['refid'])
            logger.info(post_proc)
            cur.execute(post_proc, {'folder_id': folder_info['folder_id'], 'post_step': 'id_manager_arches', 'post_info': results_id, 'ref_id': "{}_%".format(row['refid'])})
        else:
            post_proc = "INSERT INTO file_postprocessing (file_id, post_step, post_results, post_info) (SELECT file_id, %(post_step)s, 1, %(post_info)s FROM files WHERE folder_id = %(folder_id)s and file_name like %(ref_id)s) ON DUPLICATE KEY UPDATE post_results = 1".format(row['refid'])
            logger.info(post_proc)
            cur.execute(post_proc, {'folder_id': folder_info['folder_id'], 'post_step': 'id_manager_arches', 'post_info': "Link not found: {}".format(results_id), 'ref_id': "{}_%".format(row['refid'])})



cur.close()
conn.close()
