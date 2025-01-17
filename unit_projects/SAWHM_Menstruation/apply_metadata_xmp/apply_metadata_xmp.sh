#!/bin/bash
#
# Apply metadata from file and clear old metadata
#  is-sawhm_nmah-menstruation project
#

# $1 is a directory
echo "Running on $1"

rm $1/TIF/*.md5
rm $1/RAW/*.md5

exiftool -m -overwrite_original_in_place -tagsfromFile ahb_generic_ispp_mum.xmp $1/TIF/*.tif

exiftool -m -overwrite_original_in_place -Keywords="Destigmatizing Menstruation Digitization Project" -n -xmp:copyrightstatus="CS-UNK" -Sub-location="National Museum of American History" -CopyrightNotice="This media was obtained from the Smithsonian Institution. The media or its contents may be protected by international copyright laws." -Writer-Editor="National Museum of American History" $1/TIF/*.tif



# Clear old metadata in raws
exiftool -overwrite_original_in_place -Creator= -Artist= $1/RAW/*.dng

/usr/local/bin/md5tool_parallel $1 12
