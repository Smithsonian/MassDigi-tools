#!/usr/bin/env python3
#
# Extract the IRN for the taxonomy from the image metadata
# NMNH Entomology - Bees 2019 Digitization
#

##Import modules
import os, sys, subprocess, locale, logging, time, glob, shutil, re
from pathlib import Path
from subprocess import Popen,PIPE
from time import localtime, strftime
from tqdm import tqdm
from pyfiglet import Figlet



#Script variables
script_title = "Extract Taxonomy IRN Script"
subtitle = "Digitization Program Office\nOffice of the Chief Information Officer\nSmithsonian Institution\nhttps://dpo.si.edu"
ver = "0.1"
vercheck = "https://raw.githubusercontent.com/Smithsonian/MassDigi-tools/master/extract_irn_from_meta/toolversion.txt"
repo = "https://github.com/Smithsonian/MassDigi-tools/"
lic = "Available under the Apache 2.0 License"


##Set locale
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



folder_to_process = sys.argv[1]


##Set logging
if not os.path.exists('logs'):
    os.makedirs('logs')
current_time = strftime("%Y%m%d%H%M%S", localtime())
logfile = 'logs/get_irn_' + current_time + '.log'
# from http://stackoverflow.com/a/9321890
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S',
                    filename=logfile,
                    filemode='a')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
logger1 = logging.getLogger("get_irn")
logger1.info("folder_to_process: {}".format(folder_to_process))


#Test code:
#exiftool -OriginalTransmissionReference= USNMENT01725043.tif
#exiftool -TransmissionReference= USNMENT01725043.tif


def main():
    ##Save current directory
    script_dir = os.getcwd()
    os.chdir(folder_to_process)
    if not os.path.exists('export'):
        os.makedirs('export')
    path = 'export/specimens_taxonomy.csv'
    irn_file = open(path, 'w')
    irn_file.write("specimen,taxonomy_irn\n")
    files = glob.glob("*.tif")
    logger1.info("Found {} files in folder".format(len(files)))
    for file in tqdm(files):
        #Copy file
        dest = shutil.copy(file, 'export/')
        #Get irn
        p = subprocess.Popen(['exiftool', '-OriginalTransmissionReference', "export/{}".format(file)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out,err) = p.communicate()
        exif_info = out
        for line in exif_info.splitlines():
            tag = line.decode('UTF-8').replace('Original Transmission Reference :', '').strip()
            irn_file.write("{},{}\n".format(file.replace('.tif', ''), tag))
        #Remove the tag
        p = subprocess.Popen(['exiftool', '-OriginalTransmissionReference=', '-overwrite_original', "export/{}".format(file)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out,err) = p.communicate()
        if p.returncode != 0:
            logger1.error("Error with image {}: {} - {}".format(file, out, err))
        p = subprocess.Popen(['exiftool', '-TransmissionReference=', '-overwrite_original', "export/{}".format(file)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out,err) = p.communicate()
        if p.returncode != 0:
            logger1.error("Error with image {}: {} - {}".format(file, out, err))
    irn_file.close()
    os.chdir(script_dir)
    return


############################################
# Execute
############################################
if __name__=="__main__":
    main()



sys.exit(0)