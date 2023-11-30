#!/usr/bin/env python3
#
# Generate HMO IDs

import settings
import uuid
import sys
import pandas

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


refids = ["abdf9b232cdeb401ced7e386d97c013b", "a48abb18653b3f2d7ec1473e63755e6b", "a9e4073af3ac29d2d8601a8c06be5646", "da0c77f6628da9148489b5ee41786cde", "4945c6702e1495b214b24b4bbc71f460"]


for refid in refids:
    query = "SELECT * FROM jpc_aspace_data where refid = '{}'".format(refid)
    cur.execute(query)
    refid_info = cur.fetchall()

    query = "SELECT distinct SUBSTRING_INDEX(file_name, '_', 2) as sequence FROM files where folder_id in (SELECT folder_id FROM folders WHERE project_id = 186) and file_name like '{}_%'".format(refid)
    cur.execute(query)
    objects = cur.fetchall()

    insert_query = "INSERT INTO jpc_massdigi_ids (id_relationship, id1_value, id2_value) VALUES (%(id_relationship)s, %(id1_value)s, %(id2_value)s)"

    for object in objects:
        # Write the refid and create an HMO id
        id_relationship = "refid_hmo"
        hmo_id = str(uuid.uuid4())
        cur.execute(insert_query,
                            {
                                'id_relationship': id_relationship,
                                'id1_value': refid,
                                'id2_value': hmo_id
                            })

        query = "SELECT file_id, file_name from files where folder_id in (SELECT folder_id FROM folders WHERE project_id = 186) and file_name like '{}_%'".format(object['sequence'])
        cur.execute(query)
        files = cur.fetchall()

        # Write the HMO id to the filename
        id_relationship = "hmo_tif"

        for file in files:
            cur.execute(insert_query,
                            {
                                'id_relationship': id_relationship,
                                'id1_value': hmo_id,
                                'id2_value': file['file_name']
                            })
        
        # Relationship between the tif and DAMS UAN
        id_relationship = "tif_dams"

        for file in files:
            query = "SELECT dams_uan from dams_cdis_file_status_view_dpo where file_name = '{}.tif' and project_cd = 'jpc'".format(file['file_name'])
            cur.execute(query)
            damsuan = cur.fetchall()
            cur.execute(insert_query,
                            {
                                'id_relationship': id_relationship,
                                'id1_value': file['file_name'],
                                'id2_value': damsuan[0]['dams_uan']
                            })

        
cur.close()
conn.close()
