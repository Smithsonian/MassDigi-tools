#!/usr/bin/env python3
#
# Rename image using the barcode in a datamatrix 
# Version 0.1
#
# 7 Oct 2019
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
import locale, logging, os, glob, glob, sys, shutil
from pathlib import Path
from functools import partial
import webbrowser
from dpologo import dpologo
from pylibdmtx.pylibdmtx import decode
from PIL import Image
#Timing (https://stackoverflow.com/a/25823885)
from timeit import default_timer as timer




#Script variables
script_title = "Rename File from Data Matrix Tool"
subtitle = "Digitization Program Office\nOffice of the Chief Information Officer\nSmithsonian Institution\nhttps://dpo.si.edu"
ver = "0.1"
vercheck = "https://raw.githubusercontent.com/Smithsonian/MassDigi-tools/master/rename_file_from_datamatrix/toolversion.txt"
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


#Ask for the top folder
layout = [[sg.Text('Select the folder to rename the files')],
         [sg.InputText(), sg.FolderBrowse()],
         [sg.Checkbox('Save log to file', default = True)],
         [sg.Submit(), sg.Cancel()]]

window = sg.Window('Select folder', layout)
event, values = window.Read()
window.Close()

#User clicked cancel, exit program
if event == 'Cancel':
    raise SystemExit("User pressed Cancel")


folder_to_browse = values[0]
if folder_to_browse == "":
    sg.Popup('ERROR: No folder was selected\nLeaving program')
    raise SystemExit("No folder selected")
#To do: implement Path instead of manually writing paths
#folder_to_browse = Path(values[0])

save_to_log = values[1]

if save_to_log:
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
    logger1.info("folder_to_browse: {}".format(folder_to_browse))




def rename_dmcode(filepath, filename):
    image_file = filename
    if os.path.isfile(image_file) == False:
        print("Error: Could not find the file {}".format(image_file))
        sys.exit(1)
    try:
        image = Image.open(image_file)
    except Exception as e:
        print("There was an error opening the file: {}".format(e))
        sys.exit(1)
    decoded_dm = decode(image)
    decoded_data = decoded_dm[0][0].decode('ascii')
    file_extension = Path(image_file).suffix
    export_folder = "{}\\export".format(filepath)
    new_filename = "{}\\{}{}".format(export_folder, decoded_data, file_extension)
    if os.path.isdir(export_folder) == False:
        os.mkdir(export_folder)
    shutil.copy(image_file, new_filename)
    return (new_filename)




#Read JPG and/or TIF files
#using extend from https://stackoverflow.com/a/26403164
files = glob.glob("{}\\*.jpg".format(folder_to_browse))
files.extend(glob.glob("{}\\*.tif".format(folder_to_browse)))
files.extend(glob.glob("{}\\*.tiff".format(folder_to_browse)))




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
    start = timer()
    file_rename = rename_dmcode(folder_to_browse, file)
    end = timer()
    process_time = round(end - start, 2)
    res = res + "Copied file {} to {} in {} sec".format(file, file_rename, process_time) + "\n"
    if save_to_log:
        logger1.info("Copied file {} to {} in {} sec".format(file, file_rename, process_time))
    progress_bar.UpdateBar(i, len(files))
    progress_info.Update("Working on {} files...".format(len(files)))
    i += 1

    

window.Close()



#GUI info window
sg.PopupScrolled(res, title = 'Done!', size=(100, 20))

sys.exit(0)
