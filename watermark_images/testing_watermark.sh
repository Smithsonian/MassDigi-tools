#!/bin/bash
#
# Add "for testing..." statement on
#  images using imagemagick.
mkdir jpgs
mkdir tifs
mkdir raws

for i in *.jpg
      do

      convert $i -pointsize 140 \
                -draw "gravity center \
                  fill \"rgba(0,0,0,0.8)\" text 8,159 'Delete this file after 12/31/2024.' \
                  fill \"rgba(255,0,0,0.8)\"  text 0,151 'Delete this file after 12/31/2024.' \
                  fill \"rgba(0,0,0,0.8)\"  text 8,19 'For testing purposes only.' \
                  fill \"rgba(255,0,0,0.8)\"  text 0,11 'For testing purposes only.' " \
              jpgs/$i
              # Create tifs, smaller in size
              convert jpgs/$i -compress lzw tifs/${i%.jpg}.tif
              # Make raws
              convert jpgs/$i raws/${i%.jpg}.eip
done

rm *.jpg

exit 0
