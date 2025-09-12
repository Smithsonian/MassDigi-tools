#!/usr/bin/env python3
#

import sys
import mysql.connector
# Import settings from settings.py file
import settings


# Connect to Mysql 
try:
    conn = mysql.connector.connect(host=settings.host,
                            user=settings.user,
                            password=settings.password,
                            database=settings.database,
                            port=settings.port, 
                            autocommit=True, 
                            connection_timeout=60)
    conn.time_zone = '-04:00'
    cur = conn.cursor(dictionary=True)
except mysql.connector.Error as err:
    print(err)
    sys.exit(1)


cur.execute("delete from external_data where dataset_key = 'usnment_conveyor'")
    


# Insert numbers in batches
batch_size = 10000
for start in range(1, 10000001, batch_size):
    end = start + batch_size
    values = [(i,) for i in range(start, min(end, 10000001))]
    cur.executemany("INSERT INTO external_data (dataset_key, value1) VALUES ('usnment_conveyor', %s)", values)
    print(f"Inserted numbers {start} to {end - 1}")



# Close connection
cur.close()
conn.close()
