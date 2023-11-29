#!/bin/bash
#
#using imagemagick
for i in *.jpg
	do

	convert $i -resize 1920x1080 ${i%.jpg}_1.jpg
	rm $i
	mv ${i%.jpg}_1.jpg $i
	done

exit 0
