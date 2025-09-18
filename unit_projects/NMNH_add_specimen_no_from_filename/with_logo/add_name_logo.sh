#!/bin/bash
#
# Get the USNMENT number from the filename
#  and write it on each image using Imagemagick
# Version for Entomology Conveyor
# 
# v. 2025-09-17

FILE=$1

# Get the specimen number from first part of filename
USNMENT=$(echo "$FILE" | cut -d'_' -f1)

# Add USNMENT number
convert -limit thread 4 $FILE -gravity SouthEast -background white -splice 0x300 -pointsize 120 -fill black -annotate +600+300 "$USNMENT" -type truecolor -depth 8 -compress lzw export/$FILE

# Add logo on bottom-left
composite -gravity SouthEast nmnh.png export/$FILE export/$FILE

#Transfer exif data
exiftool -overwrite_original -TagsFromFile $FILE "-all:all>all:all" export/$FILE

convert export/$FILE export/${FILE%.tif}.jpg

exit 0
