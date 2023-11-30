#!/bin/bash
#
# Resize images to reduce size before sending to transcription vendor

# using imagemagick
for i in *.jpg
	do
	convert "$i" -sharpen 0x1.0 -resize 1080x1080 -quality 80 export/"$i"
	done

exit 0



