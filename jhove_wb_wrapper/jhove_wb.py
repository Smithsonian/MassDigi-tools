#!/usr/bin/env python3
#
# JHOVE White Balance wrapper
# Version 0.1
# Run this script to avoid an error from JHOVE
#   when the only issue is the white balance value.
#   JHOVE 1.20 returns an error if WB is not 0/1, but
#   cameras are using other values now. 
#
# The script returns no error, but makes a note that 
#   WB is outside the expected values.

#Import modules
import os, sys, subprocess, random, xmltodict

#Import settings from settings.py file
import settings

#System Settings
jhove_path = settings.jhove_path

def jhove_validate(filepath):
    """
    Validate the file with JHOVE
    """
    #Where to write the results
    xml_file = "/tmp/{}.xml".format(random.randint(1000, 100000))
    #Run JHOVE
    subprocess.run([jhove_path, "-m", "TIFF-hul", "-h", "xml", "-o", xml_file, filepath])
    #Open and read the results xml
    try:
        with open(xml_file) as fd:
            doc = xmltodict.parse(fd.read())
        #Delete xml file
        os.unlink(xml_file)
    except:
        return (False, "Could not find result file from JHOVE ({})".format(xml_file))
    #Get file status
    file_status = doc['jhove']['repInfo']['status']
    if file_status == "Well-Formed and valid":
        jhove_val = 0
    else:
        jhove_val = 1
        #Check if there is only one issue
        if len(doc['jhove']['repInfo']['messages']) == 1:
            #If error is with the WB, ignore
            if doc['jhove']['repInfo']['messages']['message']['#text'][:31] == "WhiteBalance value out of range":
                jhove_val = 0
            file_status = "{}; {}".format(file_status, doc['jhove']['repInfo']['messages']['message']['#text'])
    if jhove_val == 0:
        return (jhove_val, file_status)
    else: 
        return (jhove_val, file_status)


(jhove_ret, file_status) = jhove_validate(sys.argv[1])

sys.stdout.write(file_status)
sys.stdout.write('\n')
sys.stdout.flush()
sys.exit(jhove_ret)