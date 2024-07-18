#!/usr/bin/env python3
#
# Write Generators to Getty's ID Manager
#   for the Digitization Project of the 
#   JPC Archive
#
# v. 2023-10-10

import sys
import json
import requests
import settings


# Don't run automatically
sys.exit(0)




# Get token for authorized user
params = {
        "username": settings.username,
        "password": settings.password
          }
r = requests.post("{}/id-management/auth".format(settings.id_manager_url), json=params)
response_json = json.loads(r.content.decode('utf-8'))
access_token = response_json['access_token']


# Use token for all next queries by placing it in the Header of the request
Headers = {"Authorization": "Bearer {}".format(access_token)}


# From instructions:
#   A generator URI can be registered by performing an authenticated POST request to this URL, with data about it (expressed in JSON)
#   POST /id-management/generators
#   {
#      "uri": "http://....", 
#      "description": "A useful description of the URI. Important to include if the URI does not resolve."
#   }


# For Osprey
params = {
        "uri": "https://data.getty.edu/local/thesaurus/generators/osprey",
        "description": "Dashboard for Digitization Projects of the Smithsonian DPO"
        }
r = requests.post("{}/id-management/generators".format(settings.id_manager_url), json=params, headers=Headers)


# For DAMS
params = {
        "uri": "https://data.getty.edu/local/thesaurus/generators/dams",
        "description": "Smithsonian's Digital Asset Management System"
        }
r = requests.post("{}/id-management/generators".format(settings.id_manager_url), json=params, headers=Headers)
