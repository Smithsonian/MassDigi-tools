#!/usr/bin/env python3
#
# Get folders from ASpace and store the RefIDs

import json
import requests
import settings
import xml.etree.ElementTree as ET
import sys
import uuid

# MySQL
import pymysql


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
    sys.exit('System error')


params = {"password": settings.aspace_api_password}

r = requests.post("{}/users/{}/login".format(settings.aspace_api, settings.aspace_api_username), params=params)

if r.status_code == 200:
    print("\n Success! Was able to get token\n")
else:
    print("\n There was an error: {}".format(r.reason))

response_json = json.loads(r.content.decode('utf-8'))

session_token = response_json['session']

Headers = {"X-ArchivesSpace-Session": session_token}

print("\n Querying API...")

print("\n Getting Resources...")

r = requests.get("{}/repositories/2/resources?page=1".format(settings.aspace_api), headers=Headers)

list_resources = json.loads(r.text.encode('utf-8'))['results']

cur.execute("DELETE FROM jpc_aspace_resources")
cur.execute("DELETE FROM jpc_aspace_data")

for resource in list_resources:
    repository_id = resource['repository']['ref']
    resource_id = resource['ead_id']
    resource_title = resource['title']
    resource_tree = resource['tree']['ref']
    print("\n Resource ID: {}".format(resource_id))
    table_id = uuid.uuid4()
    cur.execute("INSERT INTO jpc_aspace_resources "
                "   (table_id, resource_id, repository_id, resource_title, resource_tree) "
                "VALUES "
                "   (%(table_id)s, %(resource_id)s, %(repository_id)s, %(resource_title)s, %(resource_tree)s)",
                {
                    'table_id': table_id,
                    'resource_id': resource_id,
                    'resource_title': resource_title,
                    'repository_id': repository_id,
                    'resource_tree': resource_tree
                })

    r = requests.get(
        "{}{}/resource_descriptions/{}.xml?include_unpublished=false&include_daos=true&numbered_cs=true&print_pdf=false&ead3=false".format(
            settings.aspace_api, repository_id, resource_tree.split('/')[4]), headers=Headers)

    # get root element
    tree = ET.fromstring(r.text)
    root = ET.ElementTree(tree).getroot()

    with open("{}.xml".format(resource_id.replace(":", "_")), "wb") as f:
        f.write(ET.tostring(tree))

    ns = "{urn:isbn:1-931666-22-9}"

    # Implement later more elegant
    c01_list = root.findall('.//' + ns + 'archdesc/' + ns + 'dsc/' + ns + 'c01')

    if r.status_code == 200:
        print("\n Success! Got {} records from:\n  {}\n".format(len(c01_list), r.request.url))
    else:
        print("\n There was an error: {}".format(r.reason))

    i = 0

    # Run the hierarchy, c01 -> c02 -> c03
    for c01_item in c01_list:
        try:
            # iterate child elements of item
            unit_title = c01_item.find('.//' + ns + 'did/' + ns + 'unittitle').text
            c02_items = c01_item.findall('.//' + ns + 'c02')
            for c02_item in c02_items:
                try:
                    fol_type = c02_item.find('.//' + ns + 'did/' + ns + 'unittitle').text
                except AttributeError:
                    print("109")
                    continue
                # try:
                #     refid = c02_item.find('.//' + ns + 'c03').attrib['id'].replace('aspace_', '')
                #     # Get URL
                #     r = requests.get(
                #         "{}/repositories/2/find_by_id/archival_objects?ref_id[]={};resolve[]=archival_objects".format(
                #             settings.aspace_api, refid), headers=Headers)
                #     object_json = json.loads(r.text)
                #     uri = object_json['archival_objects'][0]['ref']
                # except AttributeError:
                #     print("120")
                #     continue
                # except IndexError:
                #     print("123")
                #     continue
                try:
                    c03_items = c02_item.findall('.//' + ns + 'c03')
                except AttributeError:
                    print("128")
                    continue
                for c03_item in c03_items:
                    # refid = c03_item.find('.//' + ns + 'c03').attrib['id'].replace('aspace_', '')
                    refid = c03_item.attrib['id'].replace('aspace_', '')
                    # Get URL
                    r = requests.get(
                        "{}/repositories/2/find_by_id/archival_objects?ref_id[]={};resolve[]=archival_objects".format(
                            settings.aspace_api, refid), headers=Headers)
                    object_json = json.loads(r.text)
                    uri = object_json['archival_objects'][0]['ref']
                    creation_time = object_json['archival_objects'][0]['_resolved']['create_time']
                    creation_date = creation_time.split('T')[0]
                    mod_date = object_json['archival_objects'][0]['_resolved']['user_mtime']
                    mod_date = mod_date.split('T')[0]
                    try:
                        archive_box = c03_item.find('.//' + ns + 'did/' + ns + 'container[@type="box"]').text
                    except AttributeError:
                        try:
                            archive_box = c03_item.find('.//' + ns + 'did/' + ns + 'container[@type="Hollinger"]').text
                        except AttributeError:
                            try:
                                archive_box = c03_item.find('.//' + ns + 'did/' + ns + 'container[@type="Clamshell"]').text
                            except AttributeError:
                                try:
                                    archive_box = c03_item.find(
                                        './/' + ns + 'did/' + ns + 'container[@type="Short Lid"]').text
                                except AttributeError:
                                    try:
                                        archive_box = c03_item.find(
                                            './/' + ns + 'did/' + ns + 'container[@type="Binder"]').text
                                    except AttributeError:
                                        archive_box = ""
                    try:
                        archive_folder = c03_item.find('.//' + ns + 'did/' + ns + 'container[@type="folder"]').text
                    except AttributeError:
                        archive_folder = ""

                    print(
                        "{} - {}:{}:{}:{}:{} ({})".format(i, unit_title, fol_type, archive_box, archive_folder, refid, uri))
                    table_id = uuid.uuid4()
                    i += 1
                    cur.execute("INSERT INTO jpc_aspace_data "
                                "   (table_id, resource_id, refid, archive_box, archive_type, archive_folder, unit_title, url, creation_date, mod_date) "
                                "   VALUES "
                                "   (%(table_id)s, %(resource_id)s, %(refid)s, %(archive_box)s, %(archive_type)s, %(archive_folder)s, %(unit_title)s, %(url)s, %(creation_date)s, %(mod_date)s)"
                                "   ON DUPLICATE KEY UPDATE archive_box = %(archive_box)s, archive_type = %(archive_type)s, archive_folder = %(archive_folder)s, unit_title = %(unit_title)s, creation_date = %(creation_date)s",
                                {
                                    'table_id': table_id,
                                    'resource_id': resource_id,
                                    'refid': refid,
                                    'archive_box': archive_box,
                                    'archive_type': fol_type,
                                    'archive_folder': archive_folder,
                                    'unit_title': unit_title,
                                    'creation_date': creation_date,
                                    'mod_date': mod_date,
                                    'url': "{}{}".format(settings.public_aspace, uri)
                                })
        except:
            print("Error with {}".format(unit_title))
            continue

cur.close()
conn.close()


