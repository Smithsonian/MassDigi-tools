#!/bin/bash
#
# Fix TIFs that show with multiple pages
#

# Store files in a folder called export
mkdir export

# Assumes the first one is the one we want, verify before using
for i in *.tif; do
    convert $i[0] export/$i
done
