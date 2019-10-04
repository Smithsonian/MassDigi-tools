#!/usr/bin/env python3
#
# Extract DataMatrix barcodes from a tif image
# Version 0.1
#

from pylibdmtx.pylibdmtx import decode
from PIL import Image
import sys, os


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
    print("%s,%s" % (image_file, decoded_data))


sys.exit(0)