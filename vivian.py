import sys
import calendar
import traceback
import re
import exifread
import os
import shutil
from IPTC import IPTCInfo
 
base = '/Users/chad/Pictures'  # base dir 
rawFolder = '/Users/chad/Pictures/exif_import'  # dir where raw images from camera await import
fileExt = '.JPG'
filelist = os.listdir(rawFolder)
count = 0

def RenameFile(base, filename, rawFolder):
    try:
        picNumber = filename[len(filename)-8:len(filename)-4]
        
        # Open file, get EXIF tags, get date string and focal length
        os.chdir(rawFolder)
        f = open(filename, 'rb')
        tags = exifread.process_file(f)
        datestr = str(tags['EXIF DateTimeDigitized'])
        # Focal length
        focalLen = str(tags['EXIF FocalLength'])
        # Determine if focal length is fractional and not integer
        if focalLen.find('/') != -1:
            # If fractional, split into two halves and do the math to get an integer
            f1 = focalLen.split('/')
            focalLen = str(int(round(float(f1[0])/float(f1[1]))))
        else:
            focalLen = focalLen
       
        # Start parsing EXIF tags we just grabbed
        datestr = datestr.split(' ')
        dt = datestr[0]  # date
        tm = datestr[1]  # time
        
        # Date
        y = dt.split(':')[0]  # year
       
        if len(dt.split(':')[1]) < 2:  # month
            m = str('0') + dt.split(':')[1] 
        else:
            m = dt.split(':')[1]
           
        if len(dt.split(':')[2]) < 2:  # day
            d = str('0') + dt.split(':')[2] 
        else:
            d = dt.split(':')[2]
        
        # Time
        if int(tm.split(':')[0]) < 13:   # hour
            hr = tm.split(':')[0]
            ampm = 'AM'
        elif int(tm.split(':')[0]) > 12:
            hr = (int(tm.split(':')[0]) - 12)
            ampm = 'PM'
            
        min = tm.split(':')[1]   #  minute
        sec = tm.split(':')[2]   #  second
        
        # Establish new filename in form of:
        # 0000_yyyy-mm-dd_hh-mm-ss_00mm.jpg
        newName = picNumber + '_' + dt.replace(':', '-') + '_' + tm.replace(':', '-') + '_' + focalLen + 'mm.jpg'
    except:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n    " + \
                str(sys.exc_type)+ ": " + str(sys.exc_value) + "\n"
        print pymsg
    
    im_name = FilePic(rawFolder, base, filename, newName, y, m, d)
    AddDateInfoKeywords(im_name, rawFolder, filename, base, newName, y, m, d, hr, ampm, focalLen)

   
def GetLensType(rawFolder, filename):
    if filename[:3] == 'DSC':
        os.chdir(rawFolder)
        f = open(filename, 'rb')
        tags = exifread.process_file(f)
        lensMinMaxFocal = str(tags['MakerNote LensMinMaxFocalMaxAperture'])
        if re.match('.18',lensMinMaxFocal) != None and re.search('.*\s70',lensMinMaxFocal) != None :
            lensName = '18-70mm f/3.5-4.5G'
        elif re.match('.50',lensMinMaxFocal) != None and re.search('.*\s50',lensMinMaxFocal) != None:        
            lensName = '50mm f/1.4D'
        elif re.match('.105',lensMinMaxFocal) != None and re.search('.*\s105',lensMinMaxFocal) != None:
            lensName = '105mm f/2.8D Micro'
        elif re.match('.70',lensMinMaxFocal) != None and re.search('.*\s300',lensMinMaxFocal) != None:
            lensName = '70-300mm f/4-5.6G'
        else:
            lensName = ''
    else:
        lensName = ''
        
    return lensName

   
def FilePic(rawFolder, base, filename, newName, y, m, d): 
    try:
        if os.path.isdir(base + '/' + y) != 1:
            os.mkdir(base + '/' + y)
        if os.path.isdir(base + '/' + y + '/' + m) != 1:
            os.mkdir(base + '/' + y + '/' + m)
        if os.path.isdir(base + '/' + y + '/' + m + '/' + d) != 1:
            os.mkdir(base + '/' + y + '/' + m + '/' + d)
        # Copy file, renaming it with new filename
        shutil.copyfile(rawFolder + '/' + filename, base + '/' + y + '/' + m + '/' + d + '/' + newName)
        imageName = base + '/' + y + '/' + m + '/' + d + '/' + newName
    except:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n    " + \
                str(sys.exc_type)+ ": " + str(sys.exc_value) + "\n"
        print pymsg
    return imageName


def AddDateInfoKeywords(im_name, rawFolder, filename, base, newName, y, m, d, hr, ampm, focalLen):
    try:
        info = IPTCInfo(im_name)
        # Day of week
        intY = int(y)
        intM = int(m)
        intD = int(d)
        dd = calendar.weekday(intY, intM, intD)
        dict = {0:'Monday',1:'Tuesday',2:'Wednesday',3:'Thursday',4:'Friday',
                5:'Saturday',6:'Sunday'}
        day = dict[dd]
        # Lens name
        lens = GetLensType(rawFolder, filename)
        # Focal length
        fc = focalLen + 'mm'
        # Write our keywords to image
        info.keywords.extend(['y' + str(y), 'm' + str(m), 'd' + str(d), day, ampm, tod, lens, fc])
        info.saveAs(os.path.join(base, str(y), str(m), str(d), newName))
    except:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n    " + \
                str(sys.exc_type)+ ": " + str(sys.exc_value) + "\n"
        print pymsg

if __name__ == '__main__':
    for file in filelist:
        filename = os.path.basename(file)
        if filename[-4:] == fileExt:
            RenameFile(base, filename, rawFolder)                    
        