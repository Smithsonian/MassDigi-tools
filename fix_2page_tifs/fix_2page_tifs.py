#!/usr/bin/env python3
#
# Remove the thumbnail of tif files
#

##Import modules
import os, sys, subprocess, locale, logging, time, glob
from pathlib import Path
from subprocess import Popen,PIPE
from time import localtime, strftime
from tqdm import tqdm


##Set locale
locale.setlocale(locale.LC_ALL, 'en_US.utf8')

#Check args
if len(sys.argv) == 1:
    sys.exit("Missing path")

if len(sys.argv) > 2:
    sys.exit("Script takes a single argument")

folder_to_fix = sys.argv[1]


##Set logging
if not os.path.exists('logs'):
    os.makedirs('logs')
current_time = strftime("%Y%m%d%H%M%S", localtime())
logfile = 'logs/fix_tif_' + current_time + '.log'
# from http://stackoverflow.com/a/9321890
# set up logging to file - see previous section for more details
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S',
                    filename=logfile,
                    filemode='a')
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)
logger1 = logging.getLogger("fix_tif")


def main():
    ##Save current directory
    script_dir = os.getcwd()
    os.chdir(folder_to_fix)
    if not os.path.exists('export'):
        os.makedirs('export')
    files = glob.glob("*.tif")
    logger1.info("Found {} files in folder".format(len(files)))
    for file in tqdm(files):
        p = subprocess.Popen(['convert', '{}[0]'.format(file), "export/{}".format(file)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out,err) = p.communicate()
        if p.returncode != 0:
            logger1.error("Error with image {}: {} - {}".format(file, out, err))
            sys.exit(1)
    os.chdir(script_dir)
    return


############################################
# Main loop
############################################
if __name__=="__main__":
    main()
   


sys.exit(0)