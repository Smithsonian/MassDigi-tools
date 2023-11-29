#!/bin/bash
#
# Crop jpg files with Imagemagick
#
# Usage: ./crop_tifs.sh <directory> <width> <height> <x_offset> <y_offset>
#
# Botany: 1990x2816

cd $1

#Store files in a folder called extracted
mkdir -p extracted

for i in *.jpg; do
    echo $i
    convert -crop $2x$3+$4+$5 +repage $i extracted/$i
done
