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


"""
The Graph in arches is as explained here https://arches.readthedocs.io/en/7.2/data-model/?highlight=graph#graph-definition
a data model respenting top level objects like Visual Works, Physical Objects etc.
The id is autocreated from arches when creating the model and doesn't change, unless the Model represented by this graph,
gets deleted and re-created.
"""

GRAPH_ID: Final[str] = settings.graph_id
ARCHES_ENDPOINT: str = settings.arches_api

RESOURCES_ENDPOINT: Final[str] = f"{ARCHES_ENDPOINT}/resources"
AUTH_ENDPOINT: Final[str] = f"{ARCHES_ENDPOINT}/o/token/"
RESOURCE_URL: Final[str] = f"{ARCHES_ENDPOINT}/resource"


class TestHMO(BaseModel):
    """
    Base Class that encapsulates the fields of our test model.
    """
    id: str
    label: str
    name_label: str
    name_content: str


class Auth(BaseModel):
    access_token: str
    refresh_token: str


def auth() -> Auth:
    """
    Authentication is performed using the username, password and the client id created earlier.
    Now each request must bear the access token for any actions to be performed.
    """
    response = requests.post(
        AUTH_ENDPOINT,
        data={
            "username": settings.arches_api_username,
            "password": settings.arches_api_password,
            "grant_type": "password",
            "client_id": settings.arches_api_clientid,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    data = response.json()
    if response.status_code == 200 and "access_token" in data:
        return Auth(
            access_token=data["access_token"], refresh_token=data["refresh_token"]
        )
    else:
        raise


# Authorize user
a = auth()



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
title = "TEST TITLE 111"
folder_no = "TEST FOLDER 111"
box_no = "TEST BOX 111"
sequence = 5


# Read data model from file
f = open('jpc_data_model4.json')
json_data_model = json.load(f)
f.close()

# Replace values of TITLE
# json_data_model['label'] = title
json_data_model['identified_by'][0]['content'] = title

resource_id = uuid.uuid3(uuid.NAMESPACE_URL, id)
#json_data_model['id'] = f"urn:uuid:{resource_id}"
json_data_model['id'] = f"https://data.jpcarchive.org/object/{resource_id}"
json_data_model['identified_by'][0]['id'] = f"https://data.jpcarchive.org/object/{resource_id}/name/1"

response = requests.put(
    f"{RESOURCES_ENDPOINT}/{GRAPH_ID}/{resource_id}",
    data=json.dumps(json_data_model),
    params=(("format", "json-ld"), ("indent", 4)),
    headers={"Authorization": f"Bearer {a.access_token}"},
)

print(response.status_code)
print(response.reason)
