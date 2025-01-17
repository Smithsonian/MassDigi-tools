#!/bin/bash
#
# Remove emdash from "Creator" field
#  in NMNH Herps project
#

# $1 is a directory
echo "Running on $1"

rm $1/TIF/*.md5
rm $1/RAW/*.md5

exiftool -m -overwrite_original_in_place -Creator="Smithsonian Digitization Program Office - Imaging Services" -Artist= $1/TIF/*.tif

/usr/local/bin/md5tool_parallel $1 12
