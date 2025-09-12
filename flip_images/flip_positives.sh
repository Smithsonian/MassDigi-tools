#!/bin/bash
#
# Flip positive images using imagemagick

for i in *_pos.tif
	do
	convert $i -flop ${i%.tif}_1.tif
	rm $i
	mv ${i%.tif}_1.tif $i
	done
exit 0
