#!/bin/bash
#
# Compress tifs with Imagemagick
#

cd $1

#Store files in a folder called compressed, just in case
mkdir compressed

for i in *.tif; do
    convert -compress lzw $i compressed/$i
done
