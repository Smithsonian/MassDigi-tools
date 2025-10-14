#!/bin/bash
#
#From http://www.linuxquestions.org/questions/linux-newbie-8/script-to-remove-spaces-from-multiple-filenames-265933/

ls | grep -e "[[:alnum:]]" | \
while read i; do
    j=`echo -n "$i" | sed -e 's/ /_/'`
    mv "$i" "$j"
done
