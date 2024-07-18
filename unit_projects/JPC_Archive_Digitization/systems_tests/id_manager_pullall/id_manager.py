#!/usr/bin/env python3
#
# Grab all ids from ID Manager and update Osprey
#  to make sure data isn't being lost somewhere
# 
# Ver 2024-06-21

import json
import requests
import settings
import sys
from multiprocessing import Pool
import urllib.parse
import os

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

if not os.path.exists('logs'):
    os.makedirs('logs')

logfile = 'logs/idmanager_{}.log'.format(current_time)
logging.basicConfig(filename=logfile, filemode='a', level=logging.DEBUG,
                    format='%(levelname)s | %(asctime)s | %(filename)s:%(lineno)s | %(message)s',
                    datefmt='%y-%b-%d %H:%M:%S')
logger = logging.getLogger("idmanager")

logger.info("Starting script on {}".format(current_time))


# Get how long it takes to run
START_TIME = time.time()

NUM_CORES = settings.no_cores

params = {
        "username": settings.id_manager_username,
        "password": settings.id_manager_password
          }

r = requests.post("{}/auth".format(settings.id_manager_url), json=params)

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


# # Database
# try:
#     conn = pymysql.connect(host=settings.host,
#                            user=settings.user,
#                            passwd=settings.password,
#                            database=settings.database,
#                            port=settings.port,
#                            charset='utf8mb4',
#                            cursorclass=pymysql.cursors.DictCursor,
#                            autocommit=True)
#     conn.time_zone = '-04:00'
#     cur = conn.cursor()
# except pymysql.Error as e:
#     print(e)
#     logger.error("Error connecting to the db: {}".format(e))
#     sys.exit('System error')

# logger.info("Connected to db")

# Aspace generator
aspace_generator = "https://data.getty.edu/local/thesaurus/generators/aspace"
# Arches generator
arches_generator = "https://data.getty.edu/local/thesaurus/generators/arches"


dams_uan_prefix = "urn:dams:"
aspace_prefix = "urn:aspace:"
arches_prefix = "https://arches.jpcarchive.org/resources/"


# Queries
fileid_query = "SELECT file_id FROM files WHERE dams_uan = %(dams_uan)s"
insert_post_proc = "INSERT INTO file_postprocessing (file_id, post_step, post_results, post_info) VALUES (%(file_id)s, %(post_step)s, 0, %(post_info)s) ON DUPLICATE KEY UPDATE post_results = 0, post_info = %(post_info)s"


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

cur.execute("DELETE FROM file_postprocessing WHERE post_step = 'id_manager' and file_id in (select file_id from files where folder_id in (select folder_id from folders where project_id = 186 or project_id = 201))")
cur.execute("DELETE FROM file_postprocessing WHERE post_step = 'id_manager_arches' and file_id in (select file_id from files where folder_id in (select folder_id from folders where project_id = 186 or project_id = 201))")
cur.execute("DELETE FROM file_postprocessing WHERE post_step = 'id_manager_aspace' and file_id in (select file_id from files where folder_id in (select folder_id from folders where project_id = 186 or project_id = 201))")


cur.close()
conn.close()


# Get all groups
url_to_check = "{}/groups".format(settings.id_manager_url)
r = requests.get(url_to_check)
list_groups = list(json.loads(r.text)['groups'])
list_groups.remove(None)
no_groups = len(list_groups)
logger.info("No. of groups: {}".format(no_groups))

# for i in range(len(no_groups)):
#     if groups[i][:7] == "dpo-jpc":
#         group_id = groups[i]
#         logger.info(group_id)
#         # Pagination
#         for j in range(1, 1000):
#             group_url = "{}/groups/{}/page/{}".format(settings.id_manager_url, group_id, j)
#             r = requests.get(group_url)
#             if r.status_code == 404:
#                 break
#             else:
#                 group_data = json.loads(r.text)
#                 group_total = group_data['total']
#                 group_items = group_data['items']
#                 for item in group_items:
#                     item_id = item['id']
#                     target = item['target']
#                     body = item['body']
#                     file_name = body['id'].replace(dams_uan, "")
#                     if target['generator'] == aspace_generator:
#                         # Aspace item
#                         aspace_id = target['id'].replace(aspace_prefix, "")
#                         post_step = "id_manager_aspace"
#                     elif target['generator'] == arches_generator:
#                         # Arches item
#                         hmo_id = target['id'].replace(arches_prefix, "")
#                         post_step = "id_manager_arches"
#                     # Get the file_id
#                     cur.execute(fileid_query, {'file_name': file_name})
#                     file_id = cur.fetchall()[0]['file_id']
#                     # Save the post_processing
#                     cur.execute(insert_post_proc, {'file_id': file_id, 'post_step': post_step, 'post_info': item_id})
   

def process_group(group_id):
    # group_id = groups[i]
    if group_id[:7] != "dpo-jpc":
        return None
    else:
        logger.info("groupid: {}".format(group_id))
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
            conn.time_zone = '-04:00'
            cur = conn.cursor()
        except pymysql.Error as e:
            print(e)
            logger.error("Error connecting to the db: {}".format(e))
            sys.exit('System error')
        logger.info("Connected to db")
        # Pagination
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
                        # aspace_id = target['id'].replace(aspace_prefix, "")
                        post_step = "id_manager_aspace"
                    elif target['generator'] == arches_generator:
                        # Arches item
                        # hmo_id = target['id'].replace(arches_prefix, "")
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
    cur.close()
    conn.close()
    return True


# process each refid in parallel
pool = Pool(NUM_CORES)
results = pool.map(process_group, list_groups)


END_TIME = time.time()
TOTAL_TIME = "{} sec".format((END_TIME - START_TIME))

# print the difference between start 
# and end time in milli. secs
print("The time of execution of above program is :{}".format(TOTAL_TIME))

logger.info("Ending script on {}".format(strftime("%Y%m%d_%H%M%S", localtime())))
logger.info("Script took: {}".format(TOTAL_TIME))

sys.exit(0)
