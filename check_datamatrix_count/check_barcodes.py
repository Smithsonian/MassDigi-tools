#!/usr/bin/env python3
#
# Script to identify images with multiple barcodes
# v. 2026-04-14

import os
# For pylibdmtx
os.environ['LD_LIBRARY_PATH'] = "/usr/local/lib"

from pylibdmtx.pylibdmtx import decode
from PIL import Image
import sys

# Parallel
import multiprocessing
from p_tqdm import p_map


# Check arguments
if len(sys.argv) == 3:
    folder = sys.argv[1]
    no_workers = int(sys.argv[2])
    if multiprocessing.cpu_count() < no_workers:
        no_workers = (multiprocessing.cpu_count()) - 1
elif len(sys.argv) == 2:
    folder = sys.argv[1]
    no_workers = (multiprocessing.cpu_count()) - 1
else:
    sys.exit("Missing folder and/or no_workers arguments.\n Usage: ./check_barcodes.py [FOLDER] [NO_WORKERS]")


def check_datamatrix(tif_file):
    """ 
    Count the number of datamatrix barcodes in the image. Limit to 3 to avoid running too long.
    There should only be one that starts with 'USNMENT'. 
    """
    tif_filename = tif_file.replace("/data/project_data/ento_pollinators_labels_composites/", "")
    folder = tif_filename.split("/tifs/")[0]
    tif_filename = tif_filename.split("/tifs/")[1].replace(".tif", "")
    # Resize the image to speed things up
    barcodes = decode(Image.open(tif_file).resize((1000,1000)), max_count=2)
    no_barcodes = len(barcodes)
    if no_barcodes == 0:
        return(f"{folder},{tif_filename},{no_barcodes}")
    elif no_barcodes > 1:
        i = 0
        barcode_count = 0
        for i in range(0, len(barcodes)):
            if barcodes[i][0][:7]==b'USNMENT':
                barcode_count += 1
        if barcode_count > 1:
            return(f"{folder},{tif_filename},{barcode_count}")


files = []
for root, d_names, f_names in os.walk(folder):
    for f in f_names:
        # Add only tifs to the list
        if f[-4:].lower() == ".tif":
            files.append(os.path.join(root, f))
    # Run in parallel
    results = p_map(check_datamatrix, files, **{"num_cpus": int(no_workers)})
    filelist = [x for x in results if x is not None]
    if len(filelist) != 0:
        with open("results.csv", 'a') as fp:
            fp.write('\n'.join(filelist))


sys.exit(0)
