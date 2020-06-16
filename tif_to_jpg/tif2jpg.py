#!/usr/bin/env python3
#
# Convert TIF files to JPG mantaining a similar tree
# The source is assumed to have subfolders called 'tifs', these are NOT
#   created in the destination.
#
#
############################################
# Import modules
############################################
import os, sys, shutil, subprocess, glob
from pathlib import Path
from PIL import Image

ver = "0.1"


#Check args
if len(sys.argv) < 3:
    sys.exit("Missing arguments\n\n Usage: python3 tif2jpg.py [from_path] [to_path]")

if len(sys.argv) > 3:
    sys.exit("Too many arguments\n\n Usage: python3 tif2jpg.py [from_path] [to_path]")


path_from = sys.argv[1]
path_to = sys.argv[2]


##Save current directory
main_dir = os.getcwd()




folders = []
for entry in os.scandir(path_from):
    if entry.is_dir():
        folders.append(entry.path)
#No folders found
if len(folders) == 0:
    sys.exit(0)
#Run each folder
for folder in folders:
    folder_path = folder
    folder_name = os.path.basename(folder)
    folder_to = "{}/{}/".format(path_to, folder_name)
    #Replace double slashes
    folder_to = folder_to.replace("//", "/")
    os.mkdir(folder_to)
    os.chdir("{}/tifs/".format(folder_path))
    files = glob.glob("*.tif")
    for file in files:
        print(file)
        file_base = Path(file).stem
        im = Image.open(os.path.join(folder_path, "tifs", file))
        print(" Generating jpeg for {}...\n".format(file))
        im.save(os.path.join(folder_to, "{}.jpg".format(file_base)), "JPEG", quality=100)



sys.exit(0)