import sys
import calendar
import traceback
import re
import exifread
import os
import shutil
 
base = '/Users/chad/Pictures'  # base dir 
rawFolder = '/Users/chad/Pictures/exif_import'
fileExt = '.JPG'
filelist = os.listdir(rawFolder)
count = 0

class Vivian(object):
    def __init__(self, file):
        self.file = file

    def fetch_files(self, mount):
        self.mount = mount
        # pull list of files from box.com mount
        return files


if __name__ == '__main__':
    for file in filelist:
        filename = os.path.basename(file)
        if filename[-4:] == fileExt:
            RenameFile(base, filename, rawFolder)                    
        