#!/usr/bin/env python3

# TEST SCRIPT TO ADD NEW RECORDS USING THE NEW MODEL THAT 
# INCLUDES THE SEQUENCE

# Create stub records in Arches
# Script adapted from Getty-provided ingest script

import requests
from typing import Final
from pydantic import BaseModel
import json
import uuid
import sys


import settings_arches as settings
import archesapiclient


GRAPH_ID: Final[str] = settings.graph_id
ARCHES_ENDPOINT: str = settings.arches_api

RESOURCES_ENDPOINT: Final[str] = f"{ARCHES_ENDPOINT}/resources"
RESOURCE_URL: Final[str] = f"{ARCHES_ENDPOINT}/resource"


url = ARCHES_ENDPOINT
client_id = settings.arches_api_clientid
username = settings.arches_api_username
password = settings.arches_api_password

a_client = archesapiclient.ArchesClient(url, client_id, username, password)




# HARDCODED FOR TESTING
# Get HMO ID from database
hmo_id = str(uuid.uuid4())

# Convert id
id = "https://data.jpcarchive.org/{}".format(hmo_id)

# # TO EXPAND
# Get title, box, and folder of HMO from folder title in database
# Example:
#   title = "3T"
#   box_no = "BI-001A"
#   folder_no = "001"
#title = "TEST TITLE LJV"
title = "TEST 20231130 LJV - Box BI-002B - Folder 007-A Image 0099" 
#folder_no = "001-A"
#box_no = "BI-001B"
sequence = 99



# Read data model from file
f = open('jpc_data_model_20231130.json')
json_data_model = json.load(f)
f.close()

# Replace values of TITLE
# json_data_model['label'] = title
json_data_model['identified_by'][0]['content'] = title
json_data_model['_label'] = title

resource_id = uuid.uuid3(uuid.NAMESPACE_URL, id)
#json_data_model['id'] = f"urn:uuid:{resource_id}"
json_data_model['id'] = f"https://data.jpcarchive.org/object/{resource_id}"
json_data_model['assigned_by'][0]['assigned'][0]['value'] = sequence



record_id = a_client.put_record(graph_id=GRAPH_ID, data=json_data_model, rec_id=hmo_id)

print(hmo_id)
