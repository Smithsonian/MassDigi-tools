#!/bin/bash
#
# Extract a piece of tif files to jpg with Imagemagick
#

cd $1

#Store files in a folder called compressed, just in case
mkdir extracted

for i in *.tif; do
    convert -crop $2x$3+$4+$5 +repage $i[0] extracted/${i%.tif}.jpg
done
