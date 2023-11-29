#!/usr/bin/env python3
#
# Encode a value to a datamatrix barcode in an image
#
# From https://pypi.org/project/pylibdmtx/

from PIL import Image
import pylibdmtx.pylibdmtx as dmtx
import sys

#What to encode
id = sys.argv[1]
#Size of the image
wh = int(sys.argv[2])

encoded = dmtx.encode(id.encode('utf8'))
img = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)

#Resize to 400x400
im1 = img.resize((wh, wh), Image.NEAREST)

#Write image
im1.save(id + '.png')

print("{}.png".format(id))
