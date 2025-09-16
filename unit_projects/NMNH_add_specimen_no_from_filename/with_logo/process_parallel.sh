#!/bin/bash
#
# Get the USNMENT number from the filename
#  and write it on each image using Imagemagick

mkdir export

ls *.tif | parallel -j 8 bash add_name_logo.sh {}

exit 0
