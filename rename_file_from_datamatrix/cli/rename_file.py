#!/usr/bin/env python3
#
# Rename image using the barcode in a datamatrix 
# Version 0.1
#

from pylibdmtx.pylibdmtx import decode
from PIL import Image
import sys, os, pathlib


#Is there an argument?
if len(sys.argv) == 1:
    print("Error: Filename missing")
    sys.exit(1)
else:
    image_file = sys.argv[1]
    if os.path.isfile(image_file) == False:
        print("Error: Could not find the file %s" % (image_file))
        sys.exit(1)
    try:
        image = Image.open(image_file)
    except Exception as e:
        print("There was an error opening the file: %s" % (e))
        sys.exit(1)
    decoded_dm = decode(image)
    decoded_data = decoded_dm[0][0].decode('ascii')
    file_extension = pathlib.Path(image_file).suffix
    os.rename(image_file, "%s%s" % (decoded_data, file_extension))
    print("File %s renamed to %s%s" % (image_file, decoded_data, file_extension))


sys.exit(0)