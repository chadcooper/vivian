import sys
import exifread
import os
import shutil


class Vivian(object):
    def __init__(self, mount, file):
        self.file = file
        self.mount = mount

    def fetch_files(self):

        # pull list of files from box.com mount
        return files

    def rename_file(filename):
        picNumber = filename[len(filename)-8:len(filename)-4]

        os.chdir(rawFolder)
        with open(filename, "rb") as file_stream:
            tags = exifread.process_file(file_stream)
            datestr = str(tags["EXIF DateTimeDigitized"])
            camera_make = tags["Image Make"]
            camera_model = tags["Image Model"]

            datestr = datestr.split(' ')
            date = datestr[0]
            time = datestr[1]

            year = date.split(':')[0]

            if len(date.split(':')[1]) < 2:
                month = str('0') + date.split(':')[1]
            else:
                month = date.split(':')[1]

            if len(date.split(':')[2]) < 2:
                day = str('0') + date.split(':')[2]
            else:
                day = date.split(':')[2]

            if int(time.split(':')[0]) < 13:
                hour = time.split(':')[0]
                am_pm = 'AM'
            elif int(time.split(':')[0]) > 12:
                hour = (int(time.split(':')[0]) - 12)
                am_pm = 'PM'

            min = time.split(':')[1]
            sec = time.split(':')[2]

            # Establish new filename in form of:
            # 0000_yyyy-mm-dd_hh-mm-ss.jpg
            newName = picNumber + '_' + date.replace(':', '-') + '_' + \
                      time.replace(':', '-') + '.jpg'

            im_name = FilePic(rawFolder, base, filename, newName, year, month, day)


    def file_photo(rawFolder, base, filename, newName, year, month, day):

        if os.path.isdir(base + '/' + year) != 1:
            os.mkdir(base + '/' + year)
        if os.path.isdir(base + '/' + year + '/' + month) != 1:
            os.mkdir(base + '/' + year + '/' + month)
        if os.path.isdir(base + '/' + year + '/' + month + '/' + day) != 1:
            os.mkdir(base + '/' + year + '/' + month + '/' + day)
        shutil.copyfile(rawFolder + '/' + filename, base + '/' + year + '/' + month +
                                                    '/' + day + '/' + newName)
        imageName = base + '/' + year + '/' + month + '/' + day + '/' + newName

        return imageName

if __name__ == '__main__':
    for file in filelist:
        filename = os.path.basename(file)
        if filename[-4:] == fileExt:
            RenameFile(base, filename, rawFolder)                    
        