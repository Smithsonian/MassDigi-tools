#!/usr/bin/env python3
#
# Write IDs to Getty's ID Manager

# Ver 2024-02-06

import json
import requests
import settings
import csv
import sys
from multiprocessing import Pool, cpu_count
import numpy as np
import re

NUM_CORES = 1

from time import time as unix 
from time import sleep

params = {
        "username": settings.username,
        "password": settings.password
          }

r = requests.post("{}/id-management/auth".format(settings.id_manager_url), json=params)

response_json = json.loads(r.content.decode('utf-8'))

access_token = response_json['access_token']

Headers = {"Authorization": "Bearer {}".format(access_token)}

print("\n Posting IDs...")


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
group_id = "idmanager-test-20240312"


def sendids(data):
    results = []
    for row in data:
        data_row = row.split(',')
        print(data_row)
        dams_uan = "urn:dams:{}".format(data_row[3])
        arches_record = "https://arches.jpcarchive.org/resources/{}".format(data_row[1])
        aspace_refid = "urn:aspace:{}".format(data_row[0])
        print(dams_uan, arches_record, aspace_refid)
        # measure how long
        START_TIME = unix()
        # DAMS to ASpace
        params = {
                        "group_id": group_id,
                        "body": {"id": dams_uan, "generator": dams_generator},
                        "target": {"id": aspace_refid, "generator": aspace_generator},
                        "motivation": motivation_part_of
                        }
        r = requests.post("{}/id-management/links".format(settings.id_manager_url), json=params, headers=Headers)
        if r.status_code != 201:
            sys.exit("INSERT FAILED - DAMS-ASPACE Link")
        idmanager_time1 = unix() - START_TIME
        START_TIME = unix()
        # DAMS to Arches
        params = {
                        "group_id": group_id,
                        "body": {"id": dams_uan, "generator": dams_generator},
                        "target": {"id": arches_record, "generator": arches_generator},
                        "motivation": motivation_arches_record
                        }
        r = requests.post("{}/id-management/links".format(settings.id_manager_url), json=params, headers=Headers)
        if r.status_code != 201:
            sys.exit("INSERT FAILED - DAMS-ARCHES Link")
        idmanager_time2 = unix() - START_TIME
        results.append("{},{},{}\n".format(data_row[1], idmanager_time1, idmanager_time2))
    return "".join(results)



with open('pilot_ids_25kbalance_1ktest.csv', 'r') as f:
    rows = f.readlines()



rows_count = len(rows)
data_chunks = np.array_split(rows, NUM_CORES)

# process each chunk in parallel
pool = Pool(NUM_CORES)
results = pool.map(sendids, data_chunks)

# write out results
with open("results_{}.csv".format(NUM_CORES), "w", newline="\n") as f:
    for text_chunk in results:
        f.write(text_chunk)



# # TEST WITH THE FIRST ONE
# with open('pilot_ids_25kbalance_10test.csv', 'r') as csvfile:
#     datareader = csv.reader(csvfile)
#     for row in datareader:
#         data_row = row
#         print(data_row)
#         # "refid","hmo","tif","dams"
#         # hmo_id = "urn:osprey:{}".format(data_row[2])
#         dams_uan = "urn:dams:{}".format(data_row[3])
#         # tif_iiif_manifest = data_row[6]
#         arches_record = "https://arches.jpcarchive.org/resources/{}".format(data_row[1])
#         aspace_refid = "urn:aspace:{}".format(data_row[0])
#         print(dams_uan, arches_record, aspace_refid)
#         # measure how long
#         START_TIME = unix()
#         # DAMS to ASpace
#         params = {
#                         "group_id": group_id,
#                         "body": {"id": dams_uan, "generator": dams_generator},
#                         "target": {"id": aspace_refid, "generator": aspace_generator},
#                         "motivation": motivation_part_of
#                         }
#         r = requests.post("{}/id-management/links".format(settings.id_manager_url), json=params, headers=Headers)
#         if r.status_code != 201:
#             sys.exit("INSERT FAILED - DAMS-ASPACE Link")
#         idmanager_time1 = unix() - START_TIME
#         START_TIME = unix()
#         # DAMS to Arches
#         params = {
#                         "group_id": group_id,
#                         "body": {"id": dams_uan, "generator": dams_generator},
#                         "target": {"id": arches_record, "generator": arches_generator},
#                         "motivation": motivation_arches_record
#                         }
#         r = requests.post("{}/id-management/links".format(settings.id_manager_url), json=params, headers=Headers)
#         if r.status_code != 201:
#             sys.exit("INSERT FAILED - DAMS-ARCHES Link")
#         idmanager_time2 = unix() - START_TIME
#         f = open("id_manager.csv", "a")
#         f.write("{},{},{}\n".format(data_row[1], idmanager_time1, idmanager_time2))
#         f.close()
#         print("{},{},{}\n".format(data_row[1], idmanager_time1, idmanager_time2))


# Delete test data
r = requests.delete("{}/id-management/groups/{}".format(settings.id_manager_url, group_id), json=params, headers=Headers)

