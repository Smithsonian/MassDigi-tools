#!/usr/bin/env python3
#
# Stitch 2 images from TIF to JPG
# CLI version
# Version 0.1
#
# 22 Jan 2020
# 
# Digitization Program Office, 
# Office of the Chief Information Officer,
# Smithsonian Institution
# https://dpo.si.edu
#
#Import modules
import urllib.request
from time import localtime, strftime
import locale, logging, os, glob, glob, sys, shutil, json
from pathlib import Path
from functools import partial
from PIL import Image
#Timing (https://stackoverflow.com/a/25823885)
from timeit import default_timer as timer
import PIL.TiffImagePlugin
from tqdm import tqdm
from pyfiglet import Figlet



#Separation between images, in pixels
img_offset = 10



#Script variables
script_title = "Stitch Images Tool"
subtitle = "Digitization Program Office\nOffice of the Chief Information Officer\nSmithsonian Institution\nhttps://dpo.si.edu"
ver = "0.1"
vercheck = "https://raw.githubusercontent.com/Smithsonian/MassDigi-tools/master/stitch_images/toolversion.txt"
repo = "https://github.com/Smithsonian/MassDigi-tools/"
lic = "Available under the Apache 2.0 License"


# Set locale to UTF-8
locale.setlocale(locale.LC_ALL, 'en_US.utf8')


#Get current time
current_time = strftime("%Y%m%d_%H%M%S", localtime())



#Check args
if len(sys.argv) < 7:
    sys.exit("Missing paths. Usage:\n stitch_images.py [from] [to] [image1_suffix] [image2_suffix] [stitchedimage_suffix] [vertical or horizontal]")


#Check for updates to the script
try:
    with urllib.request.urlopen(vercheck) as response:
       current_ver = response.read()
    cur_ver = current_ver.decode('ascii').replace('\n','')
    if cur_ver != ver:
        msg_text = "{subtitle}\n\n{repo}\n\n{lic}\n\nver. {ver}\nThis version is outdated. Current version is {cur_ver}.\nPlease download the updated version at: {repo}"
    else:
        msg_text = "{subtitle}\n\n{repo}\n\n{lic}\n\nver. {ver}"
except:
    msg_text = "{subtitle}\n\n{repo}\n\n{lic}\n\nver. {ver}"
    cur_ver = ver



f = Figlet(font='slant')
print("\n")
print (f.renderText(script_title))
#print(script_title)
print(msg_text.format(subtitle = subtitle, ver = ver, repo = repo, lic = lic, cur_ver = cur_ver))


folder_from = sys.argv[1]
folder_to = sys.argv[2]
image1_suffix = sys.argv[3]
image2_suffix = sys.argv[4]
stitchedimage_suffix = sys.argv[5]
orientation = sys.argv[6]


# Logging
if os.path.isdir('logs') == False:
    os.mkdir('logs')
logfile_name = 'logs/{}.log'.format(current_time)
# from http://stackoverflow.com/a/9321890
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S',
                    filename=logfile_name,
                    filemode='a')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
logger1 = logging.getLogger("stitch")
logger1.info("arguments: {}|{}|{}|{}|{}|{}".format(folder_from, folder_to, image1_suffix, image2_suffix, stitchedimage_suffix, orientation))


if os.path.isdir(folder_from) == False:
    logger1.error("Path not found: {}".format(folder_from))
    sys.exit(1)
if os.path.isdir(folder_to) == False:
    logger1.error("Path not found: {}".format(folder_to))
    sys.exit(1)


if orientation != "vertical" and orientation != "horizontal":
    logger1.error("Orientation has to be either vertical or horizontal.")
    sys.exit(1)




def stitch_images(folder_to_save, file1, file2, file_jpg, stitch_type):
    try:
        image1 = Image.open(file1)
    except Exception as e:
        exit_msg = "ERROR: {} \nFile: {}".format(e, file1)
        sg.Popup(exit_msg)
        logger1.error(exit_msg)
        raise SystemExit(exit_msg)
    try:
        image2 = Image.open(file2)
    except Exception as e:
        exit_msg = "ERROR: {} \nFile: {}".format(e, file2)
        sg.Popup(exit_msg)
        logger1.error(exit_msg)
        raise SystemExit(exit_msg)
    (img1_w, img1_h) = image1.size
    (img2_w, img2_h) = image2.size
    if stitch_type == "automatic":
        if img1_w < img1_h:
            #Vertical
            res_image_h = max(img1_h, img2_h)
            res_image_w = img1_w + img2_w + img_offset
            res = Image.new('RGB', (res_image_w, res_image_h), color=(255,255,255))
            res.paste(im=image1, box=(0, 0))
            res.paste(im=image2, box=(img1_w + img_offset, 0))
        else:
            #Horizontal
            res_image_h = img1_h + img2_h + img_offset
            res_image_w = max(img1_w, img2_w)
            res = Image.new('RGB', (res_image_w, res_image_h), color=(255,255,255))
            res.paste(im=image1, box=(0, 0))
            res.paste(im=image2, box=(0, img1_h + img_offset))
    elif stitch_type == "vertical":
        #Horizontal
        res_image_h = img1_h + img2_h + img_offset
        res_image_w = max(img1_w, img2_w)
        res = Image.new('RGB', (res_image_w, res_image_h), color=(255,255,255))
        res.paste(im=image1, box=(0, 0))
        res.paste(im=image2, box=(0, img1_h + img_offset))
    elif stitch_type == "horizontal":
        #Vertical
        res_image_h = max(img1_h, img2_h)
        res_image_w = img1_w + img2_w + img_offset
        res = Image.new('RGB', (res_image_w, res_image_h), color=(255,255,255))
        res.paste(im=image1, box=(0, 0))
        res.paste(im=image2, box=(img1_w + img_offset, 0))
    if os.path.isfile("{}/{}".format(folder_to_save, file_jpg)) == True:
        exit_msg = "Error: Result JPG already exists {}/{}".format(folder_to_save, file_jpg)
        sg.Popup(exit_msg)
        logger1.error(exit_msg)
        raise SystemExit(exit_msg)
    res.save("{}/{}".format(folder_to_save, file_jpg), "JPEG")
    #logger1.info("File {}/{} saved".format(folder_to_save, file_jpg))
    return 0




print("\nWorking...\n")


#Get list of TIF files
files = glob.glob("{}/*{}".format(folder_from, image1_suffix))

#folder_from, folder_to, image1_suffix, image2_suffix, stitchedimage_suffix, orientation

for file in tqdm(files):
    file1 = Path(file)
    file2 = Path(file.replace(image1_suffix, image2_suffix))
    if file2.is_file() == False:
        exit_msg = "ERROR: Second image for {} ({}) was not found\nLeaving program".format(file1, file2)
        logger1.error(exit_msg)
        sys.exit(1)
    file_jpg = file1.name.replace(image1_suffix, stitchedimage_suffix)
    file_res = stitch_images(folder_to, file1, file2, file_jpg, orientation)
    if file_res != 0:
        exit_msg = "ERROR: Files do not match md5:"
        print(exit_msg)
        print(res)
        sys.exit(1)


exit_msg = "Completed!"
print(exit_msg)
logger1.info(exit_msg)
sys.exit(0)