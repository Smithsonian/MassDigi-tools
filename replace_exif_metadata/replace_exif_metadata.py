#!/usr/bin/env python3
#
# Extract the IRN for the taxonomy from the image metadata
# NMNH Entomology - Bees 2019 Digitization
#

##Import modules
import os
import sys
import subprocess
import logging
import glob
import shutil
from subprocess import Popen,PIPE
from time import strftime
from time import localtime

# Parallel
import multiprocessing
from p_tqdm import p_map

#Check args
if len(sys.argv) != 3:
    sys.exit("Missing args")

folder_to_process = sys.argv[1]
no_workers = sys.argv[2]

#Test code:
# exiftool -Keywords="NAA.1975-15; Canela (Ramkokamekrá); Apanyekrá: Kanela; Maranhão; Brazil; Bill Crocker; Myles Crocker; 35mm slides" -Subject="NAA.1975-15; Canela (Ramkokamekrá); Apanyekrá: Kanela; Maranhão; Brazil; Bill Crocker; Myles Crocker; 35mm slides" -m -overwrite_original sinaa_1975_15_00C2_003-009.tif

##Save current directory
script_dir = os.getcwd()


def replace_exif(filename):
    p = subprocess.Popen(["exiftool", "-Keywords=\"NAA.1975-15; Canela (Ramkokamekrá); Apanyekrá: Kanela; Maranhão; Brazil; Bill Crocker; Myles Crocker; 35mm slides\"", "-Subject=\"NAA.1975-15; Canela (Ramkokamekrá); Apanyekrá: Kanela; Maranhão; Brazil; Bill Crocker; Myles Crocker; 35mm slides\"", "-m", "-overwrite_original", filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out,err) = p.communicate()
    if p.returncode != 0:
        print("Error with image {}: {} - {}".format(filename, out, err))
        sys.exit(99)
    return(filename)


def main():
    os.chdir(folder_to_process)
    files = glob.glob("*.tif")
    print("Found {} files in folder".format(len(files)))
    results = p_map(replace_exif, files, **{"num_cpus": int(no_workers)})
    os.chdir(script_dir)
    return


############################################
# Execute
############################################
if __name__=="__main__":
    main()


sys.exit(0)