#!/bin/bash
#
# Script to remove x from file names
#
#From http://www.linuxquestions.org/questions/linux-newbie-8/script-to-remove-spaces-from-multiple-filenames-265933/
usage()
{
        echo "Usage: $0 [directory]"
        exit 1;
}

test -d "$1" || usage

dir="$1"

ls $dir | grep -e "[[:alnum:]]" | \
while read i; do
        j=`echo -n "$i" | sed -e 's/x//'`
        mv "$dir/$i" "$dir/$j"
done
