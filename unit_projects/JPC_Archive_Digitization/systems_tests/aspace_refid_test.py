#!/usr/bin/env python3
#
# Get folders from ASpace and store the RefIDs

import json
import requests
import settings
import xml.etree.ElementTree as ET
import sys
import uuid


params = {"password": settings.aspace_api_password}

r = requests.post("{}/users/{}/login".format(settings.aspace_api, settings.aspace_api_username), params=params)

response_json = json.loads(r.content.decode('utf-8'))

session_token = response_json['session']

Headers = {"X-ArchivesSpace-Session": session_token}

r = requests.get("{}/repositories/2/resources?page=1".format(settings.aspace_api), headers=Headers)

list_resources = json.loads(r.text.encode('utf-8'))['results']

for resource in list_resources:
    repository_id = resource['repository']['ref']
    resource_id = resource['ead_id']
    resource_title = resource['title']
    resource_tree = resource['tree']['ref']
    r = requests.get(
        "{}{}/resource_descriptions/{}.xml?include_unpublished=false&include_daos=true&numbered_cs=true&print_pdf=false&ead3=false".format(
            settings.aspace_api, repository_id, resource_tree.split('/')[4]), headers=Headers)

    # get root element
    tree = ET.fromstring(r.text)
    root = ET.ElementTree(tree).getroot()

    ns = "{urn:isbn:1-931666-22-9}"

    # Implement later more elegant
    c01_list = root.findall('.//' + ns + 'archdesc/' + ns + 'dsc/' + ns + 'c01')

    i = 0

    # Run the hierarchy, c01 -> c02 -> c03
    for c01_item in c01_list:
        # try:
        # iterate child elements of item
        refid_1 = c01_item.attrib['id']
        unit_title = c01_item.find('.//' + ns + 'did/' + ns + 'unittitle').text
        c02_items = c01_item.findall('.//' + ns + 'c02')
        for c02_item in c02_items:
            refid_2 = c02_item.attrib['id']
            try:
                fol_type = c02_item.find('.//' + ns + 'did/' + ns + 'unittitle').text
            except AttributeError:
                print(unit_title)
                print("109")
                exit
            try:
                c03_items = c02_item.findall('.//' + ns + 'c03')
            except AttributeError:
                print("129")
                print(unit_title)
                exit
            for c03_item in c03_items:
                refid_3 = c03_item.attrib['id']
                print("{}|{}|{}".format(refid_1, refid_2, refid_3))


