#!/usr/bin/env python3
#
# Check MD5 hashes
# Version 0.1
#
# 19 Dec 2019
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
import pandas as pd
import locale, logging, os, glob, glob, sys, shutil, hashlib
from pathlib import Path
from functools import partial
import webbrowser
from dpologo import dpologo
from timeit import default_timer as timer
from pathlib import Path



#Script variables
script_title = "Check MD5 Tool"
subtitle = "Digitization Program Office\nOffice of the Chief Information Officer\nSmithsonian Institution\nhttps://dpo.si.edu"
ver = "0.1"
vercheck = "https://raw.githubusercontent.com/Smithsonian/MassDigi-tools/master/check_md5/toolversion.txt"
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
layout = [[sg.Text('Select the folder to check')],
         [sg.InputText(), sg.FolderBrowse()],
         [sg.Submit(), sg.Cancel()]]

window = sg.Window('Select folder', layout)
event, values = window.Read()
window.Close()

#User clicked cancel, exit program
if event == 'Cancel':
    raise SystemExit("User pressed Cancel")




folder_to_check = values[0]



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
logger1 = logging.getLogger("check_md5")
logger1.info("folder_to_check: {}".format(folder_to_check))




if folder_to_check == "":
    exit_msg = "ERROR: No folder was selected\nLeaving program"
    sg.Popup(exit_msg)
    logger1.error(exit_msg)
    raise SystemExit("No folder selected")




def check_md5(folder_to_check):
    md5_file = glob.glob("{}/*.md5".format(folder_to_check))
    if len(md5_file) == 0:
        return 1
    if len(md5_file) > 1:
        return 2
    else:
        #read md5 file
        md5_hashes = pd.read_csv(md5_file[0], sep = ' ', header = None, names = ['md5', 'file'])
    files = glob.glob("{}/*".format(folder_to_check))
    files = [ x for x in files if '.md5' not in x ]
    for file in files:
        filename = Path(file).name
        md5_hash = hashlib.md5()
        with open(file, "rb") as f:
            # Read and update hash in chunks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                md5_hash.update(byte_block)
        file_md5 = md5_hash.hexdigest()
        if file_md5 != md5_hashes[md5_hashes.file == filename]['md5'].to_string(index=False).strip():
            return filename
    return 0



layout = [[sg.Text('Working...', key = 'working')]]
#This Creates the Physical Window
window = sg.Window('Progress Information', layout).Finalize()

res = check_md5(folder_to_check)

window.Close()

if res == 1:
    exit_msg = "ERROR: md5 file not found"
    sg.Popup(exit_msg)
    logger1.error(exit_msg)
    raise SystemExit(exit_msg)
elif res == 2:
    exit_msg = "ERROR: Multiple md5 files found"
    sg.Popup(exit_msg)
    logger1.error(exit_msg)
    raise SystemExit(exit_msg)
elif res == 0:
    exit_msg = "SUCCESS: Files match md5"
    sg.Popup(exit_msg)
    logger1.info(exit_msg)
    raise SystemExit(exit_msg)

sys.exit(0)
