#!/usr/bin/env python3
#
# Get digitized components from ASpace and store the RefIDs
#  v. 2025-02-10
#  Updated to include an XSLT3 transformation of the ASpace EAD output, so that no other changes need to be made to the current mapping from EAD2002 to Osprey.

import json
import requests
import settings
import xml.etree.ElementTree as ET
import sys
import uuid
import logging
from time import strftime
from time import localtime

# MySQL
import mysql.connector

# Saxon, for XSLT processing
from saxonche import *
    
def convert_ead(ead, xslt3_file = "aspace-to-osprey-prep.xsl"):
    with PySaxonProcessor(license=False) as saxon_proc:
        try:
            xslt30_proc = saxon_proc.new_xslt30_processor()
            executable = xslt30_proc.compile_stylesheet(stylesheet_file=xslt3_file)
            node = saxon_proc.parse_xml(xml_text=ead)
            content = executable.apply_templates_returning_string(xdm_value=node)
            return content
        except PySaxonApiError as err:
             print('Error during stylesheet compliation:', err)

def save_ead(content, filename):
    with open(filename, "w") as f:
        f.write(content)

# Logging
current_time = strftime("%Y%m%d_%H%M%S", localtime())

logfile = 'get_aspace_refids_{}.log'.format(current_time)
logging.basicConfig(filename=logfile, filemode='a', level=logging.DEBUG,
                    format='%(levelname)s | %(asctime)s | %(filename)s:%(lineno)s | %(message)s',
                    datefmt='%y-%b-%d %H:%M:%S')
logger = logging.getLogger("aspace")

logger.info("Starting script on {}".format(current_time))


# Database
try:
    conn = mysql.connector.connect(host=settings.host,
                            user=settings.user,
                            passwd=settings.password,
                            database=settings.database,
                            port=settings.port,
                            charset='utf8mb4')
    conn.autocommit = True
    cur = conn.cursor(dictionary=True)
except mysql.connector.Error as err:
    logger.error("Error connecting to MySQL: {}".format(err))
    sys.exit('System error')

params = {"password": settings.aspace_api_password}

r = requests.post("{}/users/{}/login".format(settings.aspace_api, settings.aspace_api_username), params=params)

if r.status_code == 200:
    logger.info("\n Success! Was able to get token\n")
else:
    logger.error("\n There was an error: {}".format(r.reason))
    sys.exit(1)

response_json = json.loads(r.content.decode('utf-8'))

session_token = response_json['session']

Headers = {"X-ArchivesSpace-Session": session_token}

# the following will break when there are more than 25 resources...  and there's also the issue that it will pull back EVERYTHING, when we shouldn't need everything.
# r = requests.get("{}/repositories/2/resources?page=1".format(settings.aspace_api), headers=Headers)

# as a hack, the following will get a max page size of 100, which should work in a pinch since we should never have that many at a time
# ideally, though, this should just go through the paginated results, e.g. while 'first_page' < 'last_page'...

# collections to include:
# finding_aid_status = 'Digitization'
# collections to exclude :
# /repositories/2/resources/7  = A/V:      2023.M.24-AV
# /repositories/2/resources/43 = Serials:  2023.M.24-PUB
query = '/repositories/2/search?page=1&page_size=100&q=finding_aid_status:/[Dd]igitization/-id:"/repositories/2/resources/7"-id:"/repositories/2/resources/43"&type[]=resource&fields[]=ead_id,repository,title,uri'

results = requests.get(settings.aspace_api + query, headers=Headers).json()

cur.execute("DELETE FROM jpc_aspace_resources")
logger.info(cur.statement)
cur.execute("DELETE FROM jpc_aspace_data")
logger.info(cur.statement)

for resource in results['results']:
    try:  
        repository_id = resource['repository']
        resource_id = resource['ead_id']
        resource_title = resource['title']
        resource_uri = resource['uri']
        # shouldn't be needed, but just in case this is used by the Osprey database, I'm re-adding the equivalent value here with this concat statement
        resource_tree = resource_uri + '/tree'
        logger.info("Resource ID: {}".format(resource_id))

        table_id = str(uuid.uuid4())
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
        logger.info(cur.statement)
        
        r = requests.get(
            "{}{}/resource_descriptions/{}.xml?include_unpublished=false&include_daos=true&numbered_cs=true&print_pdf=false&ead3=false".format(
                settings.aspace_api, repository_id, resource_uri.split('/')[-1]), headers=Headers)

        if r.status_code != 200:
            logger.info("There was an error: {}".format(r.reason))
            sys.exit(1)

        # change process here to supply transformed representation of the XML file.
        filename = "{}.xml".format(resource_id.replace(":", "_"))
        transformed_ead = convert_ead(r.text)
        try:
            save_ead(transformed_ead, filename)
        except:
            logger.info("Error when trying to save the EAD transformation of {}".format(resource_id))
        # here, we've just switched the old r.text from ASpace, with the new transformed_ead string from saxonche
        # get root element
        tree = ET.fromstring(transformed_ead)
        root = ET.ElementTree(tree).getroot()

    except:
        logger.info("Error when trying to cycle through the resource list.")

    ns = "{urn:isbn:1-931666-22-9}"

    # Implement later more elegant
    c01_list = root.findall('.//' + ns + 'archdesc/' + ns + 'dsc/' + ns + 'c01')
    i = 0

    # Run the hierarchy, c01 -> c02 -> c03
    for c01_item in c01_list:
        # iterate child elements of item
        unit_title = c01_item.find('.//' + ns + 'did/' + ns + 'unittitle').text
        c02_items = c01_item.findall('.//' + ns + 'c02')
        for c02_item in c02_items:
            try:
                fol_type = c02_item.find('.//' + ns + 'did/' + ns + 'unittitle').text
            except AttributeError:
                logger.error("Error finding fol_type for {}".format(unit_title))
                exit
            try:
                c03_items = c02_item.findall('.//' + ns + 'c03')
            except AttributeError:
                logger.error("Error finding c03_items for {}".format(unit_title))
                exit
            for c03_item in c03_items:
                refid = c03_item.attrib['id'].replace('aspace_', '')
                logger.info("c03 refid: {}".format(refid))
                # Get URL
                # *** Note (NEW):  the following could be retrieved from the EAD eventually... since we will be updating the EAD to include more about the CW elements as well as the Rights element
                # *** but if another API call is used, the find_by_id bit isn't needed.  you can just do a GET for the URI, e.g. 
                # ***   record_json = requests.get(aspace_api + '/repositories/2/archival_objects/5851266', headers=headers).json()
                try:
                    r = requests.get(
                        "{}/repositories/2/find_by_id/archival_objects?ref_id[]={};resolve[]=archival_objects".format(
                            settings.aspace_api, refid), headers=Headers)
                    object_json = json.loads(r.text)
                    uri = object_json['archival_objects'][0]['ref']
                except IndexError:
                    logger.error("c03_refid missing prefix: {}".format(refid))
                    if refid[:7] != "aspace_":
                        refid = "aspace_" + refid
                    r = requests.get(
                        "{}/repositories/2/find_by_id/archival_objects?ref_id[]={};resolve[]=archival_objects".format(
                            settings.aspace_api, refid), headers=Headers)
                    object_json = json.loads(r.text)
                    uri = object_json['archival_objects'][0]['ref']
                logger.error("c03_uri: {}".format(uri))
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
                                    try:
                                        archive_box = c03_item.find(
                                            './/' + ns + 'did/' + ns + 'container[@type="Slide Box"]').text
                                    except AttributeError:
                                        archive_box = ""
                logger.info("refid and box: {}:{}".format(refid, archive_box))
                try:
                    archive_folder = c03_item.find('.//' + ns + 'did/' + ns + 'container[@type="folder"]').text
                except AttributeError:
                    archive_folder = ""
                logger.info("refid archive_folder: {}:{}".format(refid, archive_folder)) 
                # Get Scope, mostly for sensitive contents
                try:
                    scopecontent = c03_item.find('.//' + ns + 'scopecontent/' + ns + 'p').text
                except AttributeError:
                    scopecontent = ""
                logger.info(
                    "{}-{}:{}:{}:{}:{} ({})".format(i, unit_title, fol_type, archive_box, archive_folder, refid, uri))
                # Content warning from ASpace
                content_warnings_string = ""
                try:
                    content_warning = object_json['archival_objects'][0]['_resolved']['content_warnings']
                    if len(content_warning) > 0:
                        content_warnings = []
                        for cwarning in content_warning:
                            if cwarning['content_warning_code'] == "cw_animal":
                                content_warnings.append("animal cruelty")
                            elif cwarning['content_warning_code'] == "cw_childabuse":
                                content_warnings.append("child abuse")
                            elif cwarning['content_warning_code'] == "cw_birth":
                                content_warnings.append("childbirth")
                            elif cwarning['content_warning_code'] == "cw_crime":
                                content_warnings.append("crime scenes")
                            elif cwarning['content_warning_code'] == "cw_deceased":
                                content_warnings.append("deceased persons")
                            elif cwarning['content_warning_code'] == "cw_graphic":
                                content_warnings.append("graphic injuries or violent content")
                            elif cwarning['content_warning_code'] == "cw_medical":
                                content_warnings.append("patients in hospitals or other medical facilities")
                            elif cwarning['content_warning_code'] == "cw_records":
                                content_warnings.append("medical records")
                            elif cwarning['content_warning_code'] == "cw_nudity":
                                content_warnings.append("nudity")
                            elif cwarning['content_warning_code'] == "cw_minors":
                                content_warnings.append("minors in potentially offensive and sensitive contexts")
                        content_warnings_string = "Images might contain: {}".format(",".join(content_warnings))
                    logger.info("content_warnings_string: {} ({})".format(content_warnings_string, refid))
                except KeyError:
                    content_warnings = ""
                table_id = str(uuid.uuid4())
                i += 1
                cur.execute("INSERT INTO jpc_aspace_data "
                            "   (table_id, resource_id, refid, archive_box, archive_type, archive_folder, unit_title, url, creation_date, mod_date, scopecontent, content_warnings) "
                            "   VALUES "
                            "   (%(table_id)s, %(resource_id)s, %(refid)s, %(archive_box)s, %(archive_type)s, %(archive_folder)s, %(unit_title)s, %(url)s, %(creation_date)s, %(mod_date)s, %(scopecontent)s, %(content_warnings_string)s)"
                            "   ON DUPLICATE KEY UPDATE archive_box = %(archive_box)s, archive_type = %(archive_type)s, archive_folder = %(archive_folder)s, unit_title = %(unit_title)s, creation_date = %(creation_date)s, scopecontent = %(scopecontent)s, content_warnings = %(content_warnings_string)s",
                            {
                                'table_id': table_id,
                                'resource_id': resource_id,
                                'refid': refid.replace("aspace_", ""),
                                'archive_box': archive_box,
                                'archive_type': fol_type,
                                'archive_folder': archive_folder,
                                'unit_title': unit_title,
                                'creation_date': creation_date,
                                'mod_date': mod_date,
                                'scopecontent': scopecontent,
                                'url': "{}{}".format(settings.public_aspace, uri),
                                'content_warnings_string': content_warnings_string
                            })
                logger.info(cur.statement)
                logger.info(cur.lastrowid)



cur.close()
conn.close()
