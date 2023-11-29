#!/bin/bash
#
# Get the USNMENT number from the filename
#  and write it on each image imagemagick


mkdir export

ls *.tif | parallel -j 8 bash add_name.sh {}


exit 0
