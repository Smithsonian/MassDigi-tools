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
from time import localtime, strftime
import pandas as pd
import locale, logging, os, glob, glob, sys, shutil, hashlib
from pathlib import Path
from functools import partial
from timeit import default_timer as timer
from pathlib import Path
from tqdm import tqdm
from pyfiglet import Figlet


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


#Check args
if len(sys.argv) == 1:
    sys.exit("Missing path")

if len(sys.argv) > 2:
    sys.exit("Script takes a single argument")


#Check for updates to the script
try:
    with urllib.request.urlopen(vercheck) as response:
       current_ver = response.read()
    cur_ver = current_ver.decode('ascii').replace('\n','')
    if cur_ver != ver:
        msg_text = "{subtitle}\n\n{repo}\n{lic}\n\nver. {ver}\nThis version is outdated. Current version is {cur_ver}.\nPlease download the updated version at: {repo}"
    else:
        msg_text = "{subtitle}\n\n{repo}\n{lic}\n\nver. {ver}"
except:
    msg_text = "{subtitle}\n\n{repo}\n{lic}\n\nver. {ver}"
    cur_ver = ver



f = Figlet(font='slant')
print("\n")
print (f.renderText(script_title))
#print(script_title)
print(msg_text.format(subtitle = subtitle, ver = ver, repo = repo, lic = lic, cur_ver = cur_ver))



folder_to_check = sys.argv[1]


print("\nChecking path {}".format(folder_to_check))

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


if os.path.isdir(folder_to_check) == False:
    logger1.error("Path not found: {}".format(folder_to_check))
    sys.exit(1)


md5_file = glob.glob("{}/*.md5".format(folder_to_check))
if len(md5_file) == 0:
    exit_msg = "ERROR: md5 file not found"
    print(exit_msg)
    logger1.error(exit_msg)
    sys.exit(1)
if len(md5_file) > 1:
    exit_msg = "ERROR: Multiple md5 files found"
    print(exit_msg)
    logger1.error(exit_msg)
    sys.exit(2)
else:
    #read md5 file
    md5_hashes = pd.read_csv(md5_file[0], sep = ' ', header = None, names = ['md5', 'file'])




def check_md5(files):
    bad_files = []
    for file in tqdm(files):
        filename = Path(file).name
        md5_hash = hashlib.md5()
        with open(file, "rb") as f:
            # Read and update hash in chunks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                md5_hash.update(byte_block)
        file_md5 = md5_hash.hexdigest()
        md5_from_file = md5_hashes[md5_hashes.file == filename]['md5'].to_string(index=False).strip()
        if file_md5 == md5_from_file:
            continue
        else:
            bad_files.append(filename) 
    if len(bad_files) > 0:
        return bad_files
    else:
        return 0


print("\nWorking...\n")




#get list of files
files = glob.glob("{}/*".format(folder_to_check))
files = [ x for x in files if '.md5' not in x ]



if len(files) != md5_hashes.shape[0]:
    logger1.error("The number of files ({}) does not match the number of lines in the md5 file ({})".format(len(files), md5_hashes.shape[0]))
    sys.exit(99)



res = check_md5(files)

if res == 0:
    exit_msg = "SUCCESS: Files match md5"
    print(exit_msg)
    logger1.info(exit_msg)
    sys.exit(0)
else:
    exit_msg = "ERROR: {} files do not match md5:".format(len(res))
    print(exit_msg)
    print(res)
    sys.exit(9)
