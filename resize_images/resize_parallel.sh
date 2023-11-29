
# Use parallel 
# 4200x4200\> resize to that maximum size, keeping aspect ratio

ls *.jpg | parallel -j 8 "convert {} -resize 4200x4200\> export/{}"
