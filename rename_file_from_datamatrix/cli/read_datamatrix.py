#!/usr/bin/env python3
#
# Extract DataMatrix barcodes from a tif image
# Version 0.1
#

from pylibdmtx.pylibdmtx import decode
from PIL import Image
import sys, os
import argparse



parser = argparse.ArgumentParser()
parser.add_argument("imagefile", help="Image file with the data matrix barcode")
parser.add_argument("-q", "--quads", dest = "quads", help="How to subdivide the image in rows and columns", required = False, type=int)
parser.add_argument("-r", "--row", dest = "row", help="Row in which the datamatrix is in", required = False, type=int)
parser.add_argument("-c", "--column", dest = "col", help="Column in which the datamatrix is in", required = False, type=int)
args = parser.parse_args()


#Is there an argument?
if args.imagefile == None:
    print("Error: Filename missing")
    sys.exit(1)
else:
    if os.path.isfile(args.imagefile) == False:
        print("Error: Could not find the file %s" % (args.imagefile))
        sys.exit(1)
    try:
        image = Image.open(args.imagefile)
    except Exception as e:
        print("There was an error opening the file: %s" % (e))
        sys.exit(1)
    if args.quads and args.row and args.col:
        if args.quads < 1 or args.row < 1 or args.col < 1:
            print("Error: Sudivisions in the image can't be zero or negative" % (args.imagefile))
            sys.exit(1)
        width, height = image.size
        #Subdivided image to make recognition faster
        row = args.row
        col = args.col
        left = (width / args.quads) * float(row - 1)
        top = (height / args.quads) * float(col - 1)
        right = (width / args.quads) + float(left)
        bottom = (height / args.quads) + float(top)
        cropped_image = image.crop((left, top, right, bottom))
        image = cropped_image
    decoded_dm = decode(image)
    if len(decoded_dm) != 0:
        decoded_data = decoded_dm[0][0].decode('ascii')
    else:
        decoded_data = "NA"
    print("%s,%s" % (args.imagefile, decoded_data))

sys.exit(0)
