#!/bin/bash
#
# Get the USNMENT number from the filename
#  and write it on each image using Imagemagick

mkdir export

ls *.tif | parallel -j 4 bash add_name_logo.sh {/}

# for i in *.tif; do
#     bash add_name_logo.sh "$i"
# done


exit 0
