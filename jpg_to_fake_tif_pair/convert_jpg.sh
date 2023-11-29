#!/bin/bash
#
# Convert JPG files to TIF and RAWs for testing
#


for i in *.jpg
	do
	convert -depth 16 -compress lzw $i ${i%.jpg}.tif
  mv ${i%.jpg}.tif tifs/
	done


for i in *.jpg
  	do
  	convert $i ${i%.jpg}.eip
    mv ${i%.jpg}.eip raws/
  	done

rm *.jpg
