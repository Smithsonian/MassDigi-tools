#!/bin/bash
#
# Get the USNMENT number from the filename
#  and write it on each image imagemagick

FILE=$1

USNMENT=${FILE%.tif}

convert -limit thread 1 $FILE -gravity South -background black -splice 0x400 -pointsize 280 -fill white -annotate +0+100 "$USNMENT" -type truecolor -depth 8 -compress lzw export/$FILE

#Transfer exif data
exiftool -overwrite_original -TagsFromFile $FILE "-all:all>all:all" export/$FILE


exit 0
