#!/bin/bash
#

#JHOVE WB wrapper
for i in test/*.tif; do

    start=$(date +%s.%N)
    ./jhove_wb.py $i
    end=$(date +%s.%N)

    runtime=$( echo "scale=3; (${end} - ${start})*1000/1" | bc )
    echo "jhove_wb,$runtime" >> results.txt
    
done


#JHOVE
for i in test/*.tif; do

    start=$(date +%s.%N)
    /home/ljvillanueva/jhove/jhove $i > /dev/null
    end=$(date +%s.%N)

    runtime=$( echo "scale=3; (${end} - ${start})*1000/1" | bc )
    echo "jhove,$runtime" >> results.txt
    
done



#magick
for i in test/*.tif; do

    start=$(date +%s.%N)
    identify -verbose $i > /dev/null
    end=$(date +%s.%N)

    runtime=$( echo "scale=3; (${end} - ${start})*1000/1" | bc )
    echo "magick,$runtime" >> results.txt
    
done
