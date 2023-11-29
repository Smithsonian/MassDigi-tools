#!/usr/bin/env python3
#
# Process the files from IS project of the Botany collex
#

import subprocess
import cv2

# Settings
from_dir = ""
to_dir = ""
colorbar_image = "colorbar.tif"
logo_file = "new_logo_SI_US.tif"

filename = sys.argv[1]

# Rsync the files from the workstation to server storage
# subprocess.call(["rsync", "-av", "--delete", from_dir, to_dir])

# Find colorbar, inspired in https://stackoverflow.com/a/15147009
method = cv2.TM_SQDIFF_NORMED

# Read the images from the file
cb_image = cv2.imread(colorbar_image)
main_image = cv2.imread(filename)
logo_image = cv2.imread(logo_file)

result = cv2.matchTemplate(cb_image, main_image, method)

# We want the minimum squared difference
mn, _, mnLoc, _ = cv2.minMaxLoc(result)

# Extract the coordinates of our best match
MPx, MPy = mnLoc

# Step 2: Get the size of the colorbar
cb_size_y, cb_size_x = cb_image.shape[:2]

offset_y = MPy + cb_size_y
offset_x = MPx  # + cb_size_x

main_image_y, main_image_x = main_image.shape[:2]

cropped_logo = logo_image[0:main_image_y - offset_y - 10, 0:main_image_x - offset_x]

paste_location = [offset_y + 10, MPx]

cropped_logo_size = cropped_logo.shape[:2]

main_image[paste_location[0]:paste_location[0] + cropped_logo_size[0], paste_location[1]:paste_location[1] + cropped_logo_size[1]] = cropped_logo

# Crop full image
export_image = main_image[0:main_image_y, 0:paste_location[1] + cb_size_x + 10]

cv2.imwrite("test_full.tif", export_image)
