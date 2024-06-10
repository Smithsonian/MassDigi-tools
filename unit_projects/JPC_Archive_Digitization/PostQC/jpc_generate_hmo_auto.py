#!/usr/bin/env python3
#
# Generate HMO IDs automatically after folder passes QC

# Ver 2024-05-02

import settings
import uuid
import sys

import logging
from time import strftime
from time import localtime

# MySQL
import pymysql

if len(sys.argv) != 2:
    # Missing arg?
    print("Missing folder name")
    sys.exit(1)


project_folder = sys.argv[1]



# Logging
current_time = strftime("%Y%m%d_%H%M%S", localtime())

logfile = 'generatehmo_{}.log'.format(current_time)
logging.basicConfig(filename=logfile, filemode='a', level=logging.DEBUG,
                    format='%(levelname)s | %(asctime)s | %(filename)s:%(lineno)s | %(message)s',
                    datefmt='%y-%b-%d %H:%M:%S')
logger = logging.getLogger("hmo")

logger.info("Starting script on {}".format(current_time))



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
    logger.error("Error connecting to the db: {}".format(e))
    sys.exit('System error')


logger.info("Connected to db")

query = "SELECT * FROM folders WHERE project_id = 201 and project_folder = %(project_folder)s"
cur.execute(query, {'project_folder': project_folder})
folder_info = cur.fetchall()[0]
folder_id = folder_info['folder_id']
logger.info("folder_id: {}".format(folder_id))

get_refids = """SELECT 
                    distinct SUBSTRING_INDEX(f.file_name, '_', 1) as refid 
                FROM 
                    files f, 
                    qc_folders q,
                    folders fol
                WHERE 
                    f.folder_id = q.folder_id AND 
                    q.qc_status = 0 AND 
                    f.folder_id = fol.folder_id AND
                    fol.delivered_to_dams = 0 AND
                    SUBSTRING_INDEX(f.file_name, '_', 1) NOT IN (SELECT DISTINCT id1_value FROM jpc_massdigi_ids where id_relationship = 'refid_hmo') AND 
                    f.folder_id = %(folder_id)s"""
cur.execute(get_refids, {'folder_id': folder_id})
list_refids = cur.fetchall()


for refid in list_refids:
    refid = refid['refid']
    logger.info("refid: {}".format(refid))
    
    query = "SELECT * FROM jpc_aspace_data where refid = %(refid)s"
    cur.execute(query, {'refid': refid})
    refid_info = cur.fetchall()

    if len(refid_info) == 1:
        query = "SELECT distinct SUBSTRING_INDEX(file_name, '_', 2) as sequence FROM files where folder_id in (SELECT folder_id FROM folders WHERE project_id = 201) and file_name like '{}_%'".format(refid)
        cur.execute(query)
        objects = cur.fetchall()

        insert_query = "INSERT INTO jpc_massdigi_ids (id_relationship, id1_value, id2_value) VALUES (%(id_relationship)s, %(id1_value)s, %(id2_value)s)"

        for object in objects:
            logger.info("object: {}".format(object))
            # Write the refid and create an HMO id
            id_relationship = "refid_hmo"
            hmo_id = str(uuid.uuid4())
            cur.execute(insert_query,
                                {
                                    'id_relationship': id_relationship,
                                    'id1_value': refid,
                                    'id2_value': hmo_id
                                })

            query = "SELECT file_id, file_name, dams_uan from files where folder_id = {} and file_name like '{}_%'".format(folder_id, object['sequence'])
            cur.execute(query)
            files = cur.fetchall()

            for file in files:
                # Write the HMO id to the filename
                id_relationship = "hmo_tif"

                cur.execute(insert_query,
                                {
                                    'id_relationship': id_relationship,
                                    'id1_value': hmo_id,
                                    'id2_value': file['file_name']
                                })
            
                # Relationship between the tif and DAMS UAN
                id_relationship = "tif_dams"

                cur.execute(insert_query,
                                {
                                    'id_relationship': id_relationship,
                                    'id1_value': file['file_name'],
                                    'id2_value': file['dams_uan']
                                })
    else:
        logger.error("refid not found: {}".format(refid))
        
cur.close()
conn.close()
