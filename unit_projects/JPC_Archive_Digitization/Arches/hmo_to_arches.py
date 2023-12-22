#!/usr/bin/env python3

# Create stub records in Arches
# Script adapted from Getty-provided ingest script

import requests
from typing import Final
from pydantic import BaseModel
# from typing import Tuple
import json
import uuid
import sys

import settings_arches
import archesapiclient

# MySQL
import pymysql

import settings


"""
The Graph in arches is as explained here https://arches.readthedocs.io/en/7.2/data-model/?highlight=graph#graph-definition
a data model respenting top level objects like Visual Works, Physical Objects etc.
The id is autocreated from arches when creating the model and doesn't change, unless the Model represented by this graph,
gets deleted and re-created.
"""

GRAPH_ID: Final[str] = settings_arches.graph_id
ARCHES_ENDPOINT: str = settings_arches.arches_api

RESOURCES_ENDPOINT: Final[str] = f"{ARCHES_ENDPOINT}/resources"
RESOURCE_URL: Final[str] = f"{ARCHES_ENDPOINT}/resource"



url = ARCHES_ENDPOINT
client_id = settings_arches.arches_api_clientid
username = settings_arches.arches_api_username
password = settings_arches.arches_api_password

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


# Run query
# query = ("with data as (SELECT id1_value as refid, id2_value as hmo FROM dpo_osprey.jpc_massdigi_ids where id_relationship = 'refid_hmo') "
#             " select d.*, j.unit_title, j.archive_box, j.archive_folder "
#             " from data d, jpc_aspace_data j where d.refid=j.refid")
query = ("""
            with data as (SELECT id1_value as refid, id2_value as hmo FROM dpo_osprey.jpc_massdigi_ids 
					where id_relationship = 'refid_hmo') 
             select d.*, 
             concat(j.unit_title, ' - Box ', j.archive_box, ' Folder ', j.archive_folder, ' Item ', 
             		LPAD(	
             		row_number() over (partition by refid order by d.refid, hmo),
             		4, '0')
             			) as unit_title, 
             j.archive_box, j.archive_folder 
             from data d, jpc_aspace_data j where d.refid=j.refid
             order by unit_title
             """)

cur.execute(query)

data = cur.fetchall()

# query_insert = ("INSERT INTO jpc_massdigi_ids (id_relationship, id1_value, id2_value) "
#            "VALUES ('hmo_arches', %(hmo)s, %(arches)s)")


for row in data:
    # Get HMO ID from database
    hmo_id = row['hmo']

    # Get filename from db to get sequence
    # cur.execute("SELECT id2_value from jpc_massdigi_ids WHERE id_relationship = 'hmo_tif' and id1_value = %(hmo_id)s", {'hmo_id': hmo_id})
    # res = cur.fetchall()

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

    print(hmo_id)

    # cur.execute(query_insert, {'hmo': hmo_id, 'arches': str(resource_id)})


cur.close()
conn.close()
