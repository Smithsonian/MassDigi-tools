#!/usr/bin/env python3
#
# Autocrop images based on a corner pixel
# Version 0.3
# 2021-12-13
#
# Import required modules
from PIL import Image, ImageChops
from os.path import exists
import os
import sys


# Code inspired by https://stackoverflow.com/a/48605963
def trim(im, corner, edge_size):
    if corner == "top-left":
        bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    elif corner == "top-right":
        bg = Image.new(im.mode, im.size, im.getpixel((im.size[0] - 1, 0)))
    elif corner == "bottom-left":
        bg = Image.new(im.mode, im.size, im.getpixel((0, im.size[1] - 1)))
    elif corner == "bottom-right":
        bg = Image.new(im.mode, im.size, im.getpixel((im.size[0] - 1, im.size[1] - 1)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if edge_size != 0:
        bbox2 = (bbox[0] - edge_size, bbox[1] - edge_size, bbox[2] + edge_size, bbox[3] + edge_size)
        return im.crop(bbox2)
    else:
        return im.crop(bbox)


# Try cropping and small rotations
def autocrop(filename, which_corner, edge_size):
    # Add iterative way to choose best rotation instead of hardcoded
    img = Image.open(filename)
    # Basic trim
    new_im = trim(img, which_corner, edge_size)
    # Rotate
    rotated_1 = img.rotate(0.1)
    new_im_1 = trim(rotated_1, which_corner, edge_size)
    # Rotate in the other direction
    rotated_2 = img.rotate(-0.1)
    new_im_2 = trim(rotated_2, which_corner, edge_size)
    if new_im.size[0] < new_im_1.size[0] and new_im.size[0] < new_im_2.size[0]:
        # No rotation
        return new_im
    else:
        if new_im_1.size[0] < new_im_2.size[0]:
            # First
            return new_im_1
        else:
            return new_im_2


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Error: arguments missing. Usage:\n\n ./autocrop.py <image> <corner: top-left top-right bottom-left or "
              "bottom-right> <edge_size: integer>")
        sys.exit(1)
    else:
        filename = sys.argv[1]
        which_corner = sys.argv[2]
        edge_size = int(sys.argv[3])
        if not exists(filename):
            print("File was not found.")
            sys.exit(99)
        if which_corner not in ['top-left', 'top-right', 'bottom-left', 'bottom-right']:
            print("corner argument was not valid.")
            sys.exit(99)
        if not isinstance(edge_size, int):
            print("edge_size argument was not valid.")
            sys.exit(99)

    new_im = autocrop(filename, which_corner, edge_size)
    if not os.path.exists("output"):
        os.mkdir("output")
    new_im.save("output/{}".format(filename))
