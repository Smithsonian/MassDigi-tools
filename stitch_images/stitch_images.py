#!/usr/bin/env python3
#
# Stitch 2 images from TIF to JPG
# Version 0.1
#
# 8 Oct 2019
# 
# Digitization Program Office, 
# Office of the Chief Information Officer,
# Smithsonian Institution
# https://dpo.si.edu
#
#Import modules
import urllib.request
import PySimpleGUI as sg
from time import localtime, strftime
import locale, logging, os, glob, glob, sys, shutil, json
from pathlib import Path
from functools import partial
import webbrowser
from dpologo import dpologo
from PIL import Image
#Timing (https://stackoverflow.com/a/25823885)
from timeit import default_timer as timer
import PIL.TiffImagePlugin



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



#GUI info window
github_text = "Go to Github"
layout = [
            [sg.Image(data = dpologo)],
            [sg.Txt('_'  * 48)], 
            [sg.Text(script_title, font=(20))],
            [sg.Text(msg_text.format(subtitle = subtitle, ver = ver, repo = repo, lic = lic, cur_ver = cur_ver))],
            [sg.Submit("OK"), sg.Cancel(github_text)]]
window = sg.Window("Info", layout)
event, values = window.Read()
window.Close()

# Open browser to Github repo if user clicked the "Go to Github" button
if event == github_text:
    webbrowser.open_new_tab(repo)
    raise SystemExit("Cancelling: going to repo")

if event == None:
    #User closed window, leave program
    raise SystemExit("Leaving program")



#Check for settings file
if os.path.isfile("settings.json"):
    try:
        with open('settings.json') as json_file:
            settings = json.load(json_file)
    except:
        settings = {}
        settings['folder_to_browse'] = os.getcwd()
        settings['folder_to_save'] = None
        settings['file_pattern_1'] = "_A.tif"
        settings['file_pattern_2'] = "_B.tif"
        settings['res_file_pattern'] = "_C.jpg"
        settings['stitch_automatic'] = True
        settings['stitch_horizontal'] = False
        settings['stitch_vertical'] = False
        with open('settings.json', 'w') as outfile:
            json.dump(settings, outfile)
else:
    settings = {}
    settings['folder_to_browse'] = os.getcwd()
    settings['folder_to_save'] = None
    settings['file_pattern_1'] = "_A.tif"
    settings['file_pattern_2'] = "_B.tif"
    settings['res_file_pattern'] = "_C.jpg"
    settings['stitch_automatic'] = True
    settings['stitch_horizontal'] = False
    settings['stitch_vertical'] = False
    with open('settings.json', 'w') as outfile:
        json.dump(settings, outfile)



#Ask for the top folder
layout = [[sg.Text('Select the folder with the TIF files')],
         [sg.InputText(settings['folder_to_browse']), sg.FolderBrowse()],
         [sg.Text('Select the folder to save the stitched JPG files')],
         [sg.InputText(settings['folder_to_save']), sg.FolderBrowse()],
         [sg.T('First file suffix:'), sg.InputText(settings['file_pattern_1'], key = 'fp1')],
         [sg.T('Second file suffix:'), sg.InputText(settings['file_pattern_2'], key = 'fp2')],
         [sg.T('JPG file suffix:'), sg.InputText(settings['res_file_pattern'], key = 'fp3')],
         [sg.Text('Stitch files:'),
                sg.Radio('automatic', 'stitch', key = 'automatic', default = settings['stitch_automatic']),
                sg.Radio('horizontal', 'stitch', key = 'horizontal', default = settings['stitch_horizontal']),
                sg.Radio('vertical', 'stitch', key = 'vertical', default = settings['stitch_vertical'])                
                ],
         [sg.Submit(), sg.Cancel()]]

window = sg.Window('Select folder', layout)
event, values = window.Read()
window.Close()

#User clicked cancel, exit program
if event == 'Cancel':
    raise SystemExit("User pressed Cancel")





settings = {}
settings['folder_to_browse'] = values[0]
settings['folder_to_save'] = values[1]
settings['file_pattern_1'] = values['fp1']
settings['file_pattern_2'] = values['fp2']
settings['res_file_pattern'] = values['fp3']
settings['stitch_automatic'] = values['automatic']
settings['stitch_horizontal'] = values['horizontal']
settings['stitch_vertical'] = values['vertical']

with open('settings.json', 'w') as outfile:
    json.dump(settings, outfile)

if settings['stitch_automatic'] == True:
    stitch_type = 'automatic'
elif settings['stitch_horizontal'] == True:
    stitch_type = 'horizontal'
elif settings['stitch_vertical'] == True:
    stitch_type = 'vertical'



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
logger1 = logging.getLogger("rename_dm")
logger1.info("folder_to_browse: {}".format(settings['folder_to_browse']))




if settings['folder_to_browse'] == "":
    exit_msg = "ERROR: No folder was selected\nLeaving program"
    sg.Popup(exit_msg)
    logger1.error(exit_msg)
    raise SystemExit("No folder selected")
#To do: implement Path instead of manually writing paths
#folder_to_browse = Path(values[0])

if settings['folder_to_save'] == "":
    exit_msg = "ERROR: No folder was selected to save the files\nLeaving program"
    sg.Popup(exit_msg)
    logger1.error(exit_msg)
    raise SystemExit("No save folder selected")






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
    logger1.info("File {}/{} saved".format(folder_to_save, file_jpg))
    return file_jpg



#Get list of TIF files
files = glob.glob("{}/*{}".format(settings['folder_to_browse'], settings['file_pattern_1']))



layout = [[sg.Text('Working on {} files...'.format(len(files)), key = 'working')],
              [sg.ProgressBar(1, orientation='h', size=(20, 20), key='progress')],
          ]
#This Creates the Physical Window
window = sg.Window('Progress Information', layout).Finalize()
progress_bar = window.FindElement('progress')
progress_info = window.FindElement('working')
progress_bar.UpdateBar(0, len(files))


res = ""
i = 1
for file in files:
    file1 = Path(file)
    print(file1)
    start = timer()
    file2 = Path(file.replace(settings['file_pattern_1'], settings['file_pattern_2']))
    print(file2)
    if file2.is_file() == False:
        exit_msg = "ERROR: Second image for {} ({}) was not found\nLeaving program".format(file1, file2)
        sg.Popup(exit_msg)
        logger1.error(exit_msg)
        raise SystemExit(exit_msg)
    file_jpg = file1.name.replace(settings['file_pattern_1'], settings['res_file_pattern'])
    print(file_jpg)
    file_res = stitch_images(settings['folder_to_save'], file1, file2, file_jpg, stitch_type)
    end = timer()
    process_time = round(end - start, 2)
    stitch_msg = "Stitched {} and {} to {} in {} sec".format(file1, file2, file_res, process_time)
    res = res + stitch_msg + "\n"
    logger1.info(stitch_msg)
    progress_bar.UpdateBar(i, len(files))
    progress_info.Update("Working on {} files...".format(len(files)))
    i += 1


window.Close()


#GUI info window
sg.PopupScrolled(res, title = 'Done!', size=(100, 20))

sys.exit(0)
