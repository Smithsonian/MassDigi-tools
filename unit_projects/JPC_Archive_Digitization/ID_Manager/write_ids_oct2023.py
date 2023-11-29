#!/usr/bin/env python3
#
# Write IDs to Getty's ID Manager

# Ver 2023-10-10

import json
import requests
import settings
import csv



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




# TEST WITH THE FIRST ONE
with open('pre-pilot-ids-oct2023.csv', 'r') as csvfile:
    datareader = csv.reader(csvfile)
    for row in datareader:
        data_row = row
        print(data_row[4])
        #
        hmo_id = "urn:osprey:{}".format(data_row[2])
        dams_uan = "urn:dams:{}".format(data_row[4])
        # tif_iiif_manifest = data_row[6]
        arches_record = "https://arches.jpcarchive.org/resources/{}".format(data_row[7])
        aspace_refid = "urn:aspace:{}".format(data_row[5])
        # Oct 2023- Based on Ben's doc
        #  All use DAMS as Generator 
        # DAMS to Osprey - Needed?
        # params = {
                # "body": {"id": dams_uan, "generator": dams_generator},
                # "target": {"id": hmo_id, "generator": osprey_generator},
                # "motivation": motivation_part_of
                # }
        # r = requests.post("{}/id-management/links".format(settings.id_manager_url), json=params, headers=Headers)
        
        # DAMS to ASpace
        params = {
                "body": {"id": dams_uan, "generator": dams_generator},
                "target": {"id": aspace_refid, "generator": aspace_generator},
                "motivation": motivation_part_of
                }
        r = requests.post("{}/id-management/links".format(settings.id_manager_url), json=params, headers=Headers)
        
        # DAMS to Arches
        params = {
                "body": {"id": dams_uan, "generator": dams_generator},
                "target": {"id": arches_record, "generator": arches_generator},
                "motivation": motivation_arches_record
                }
        r = requests.post("{}/id-management/links".format(settings.id_manager_url), json=params, headers=Headers)
        #
        #
        # OLDER VERSION:
        # hmo_iiif_manifest = data_row[8]
        #
        #HMO to DAMS
        # params = {
                # "body": {"id": hmo_id, "generator": osprey_generator},
                # "target": {"id": dams_uan, "generator": dams_generator},
                # "motivation": hmo_image_motivation
                # }
        # r = requests.post("{}/id-management/links".format(settings.id_manager_url), json=params, headers=Headers)
        
        # DAMS to IIIF Manifest of tifs
        # params = {
                # "body": {"id": dams_uan, "generator": dams_generator},
                # "target": {"id": tif_iiif_manifest, "generator": edan_generator},
                # "motivation": iiif_manifest_images_motivation
                # }
        # r = requests.post("{}/id-management/links".format(settings.id_manager_url), json=params, headers=Headers)
        #
        #HMO to arches
        # params = {
                # "body": {"id": hmo_id, "generator": osprey_generator},
                # "target": {"id": arches_record, "generator": arches_generator},
                # "motivation": "https://data.getty.edu/thesaurus/motivations/arches_record"
                # }
        # r = requests.post("{}/id-management/links".format(settings.id_manager_url), json=params, headers=Headers)
        #
        # Aspace - Connect the HMO ids to the ASpace RefID
        # params = {
                # "body": {"id": hmo_id, "generator": osprey_generator},
                # "target": {"id": aspace_refid, "generator": aspace_generator},
                # "motivation": aspace_motivation
                # }
        # r = requests.post("{}/id-management/links".format(settings.id_manager_url), json=params, headers=Headers)
        # IIIF of HMO
