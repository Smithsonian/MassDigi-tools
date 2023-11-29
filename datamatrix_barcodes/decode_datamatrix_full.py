#!/usr/bin/env python3
# 
# Decode a datamatrix barcode in an image and return the value and coords
#
from pylibdmtx.pylibdmtx import decode
from PIL import Image
import sys

#Get what to encode from the command line
img_file = sys.argv[1]

img_data = decode(Image.open(img_file))

print("{},{},{},{},{},{}".format(img_file, img_data[0].data.decode('UTF-8'), img_data[0].rect.left, img_data[0].rect.top, img_data[0].rect.width, img_data[0].rect.height))
