#!/usr/bin/env python3
#
# Autocrop images
# Version 0.1
#
#Import modules
from PIL import Image, ImageChops
import os, sys

#Import settings from settings.py file
#import settings

edge_size = 10

#Code inspired by https://stackoverflow.com/a/48605963
def trim(im, edge_size):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if edge_size != 0:
        bbox2 = (bbox[0] - edge_size, bbox[1] - edge_size, bbox[2] + edge_size, bbox[3] + edge_size)
        return(im.crop(bbox2))
    else:
        return(im.crop(bbox))


# if __name__ == "__main__":
#     bg = Image.open("test.jpg") # The image to be cropped
#     new_im = trim(bg)
#     new_im.save("test2.jpg")


img = Image.open("test.jpg") # The image to be cropped
new_im = trim(img, 0)

rotated_1 = img.rotate(0.1)
new_im_1 = trim(rotated_1, 0)

rotated_2 = img.rotate(-0.1)
new_im_2 = trim(rotated_2, 0)


new_im.size
new_im_1.size
new_im_2.size



new_im.save("test2.jpg")

new_im.save("test2.jpg")
new_im_2.save("test2_2.jpg")

