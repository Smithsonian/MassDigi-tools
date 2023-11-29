#!/usr/bin/env python3
#
# Convert TIF files to JPG mantaining a similar tree
#
#
############################################
# Import modules
############################################
import os
import sys
import shutil
import subprocess
import glob
from pathlib import Path
from PIL import Image


ver = "0.2"


# Check args
if len(sys.argv) < 3:
    sys.exit("Missing arguments\n\n Usage: python3 tif2jpg.py [from_path] [to_path]")

if len(sys.argv) > 3:
    sys.exit("Too many arguments\n\n Usage: python3 tif2jpg.py [from_path] [to_path]")


path_from = sys.argv[1]
path_to = sys.argv[2]

# Save current directory
main_dir = os.getcwd()


files = glob.glob("{}/*.tif".format(path_from))
for file in files:
    print(file)
    file_base = Path(file).stem
    img = Image.open(file)
    print(" Generating jpeg for {}...\n".format(file))
    img.save(os.path.join(path_to, "{}.jpg".format(file_base)), "JPEG", quality=90, icc_profile=img.info.get('icc_profile'))


sys.exit(0)