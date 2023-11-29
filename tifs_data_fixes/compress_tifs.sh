#!/bin/bash
#
# Compress tifs with Imagemagick
#

# Store files in a folder called export, just in case
mkdir export

# Compress using LZW
for i in *.tif; do
    convert -compress lzw $i export/$i
done
