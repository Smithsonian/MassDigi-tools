#!/bin/bash
#
# Convert CR2 raw files to DNG using Imagemagick
#

for i in *.CR2; do
    convert $i -set colorspace aRGB ${i%.png}.DNG
done
