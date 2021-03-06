import sys
import EXIF
import os
import shutil
import logging
import logging.handlers
import datetime
import struct


class Logger(object):
    def __init__(self, dest):
        self.log_filename = os.path.join(dest, "vivian.log")


    def create_logger(self):
        log = logging.getLogger("vivi_logger")
        log.setLevel(logging.DEBUG)
        handler = logging.handlers.RotatingFileHandler(self.log_filename,
                                                       maxBytes=20000,
                                                       backupCount=5)
        frmt = logging.Formatter("%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s")
        handler.setFormatter(frmt)
        log.addHandler(handler)

        return log


class Vivian(object):
    def __init__(self, src, dest):
        self.src = src
        self.dest = dest
        self.dups_dir = "dups"
        logger = Logger(self.dest)
        self.log = logger.create_logger()


    def fetch_files(self):
        files = os.listdir(self.src)
        return files


    def get_video_date(self, filename):
        ATOM_HEADER_SIZE = 8
        # Difference between Unix epoch and QuickTime epoch, in seconds
        EPOCH_ADJUSTER = 2082844800
        f = open(filename, "rb")
        while 1:
            atom_header = f.read(ATOM_HEADER_SIZE)
            if atom_header[4:8] == 'moov':
                break
            else:
                atom_size = struct.unpack(">I", atom_header[0:4])[0]
                f.seek(atom_size - 8, 1)
        # Found 'moov', look for 'mvhd' and timestamps
        atom_header = f.read(ATOM_HEADER_SIZE)
        if atom_header[4:8] == 'cmov':
            self.log.info("moov atom is compressed")
        elif atom_header[4:8] != 'mvhd':
            self.log.info("expected to find 'mvhd' header")
        else:
            f.seek(4, 1)
            creation_date = struct.unpack(">I", f.read(4))[0]
            modification_date = struct.unpack(">I", f.read(4))[0]
            video_cdate = datetime.datetime.utcfromtimestamp(creation_date - EPOCH_ADJUSTER)
            formatted_date = datetime.datetime.strftime(video_cdate, "%Y-%m-%d_%I-%M-%S_%p")
            self.year = str(datetime.datetime.strftime(video_cdate, "%Y"))
            self.month = str(datetime.datetime.strftime(video_cdate, "%m"))
            self.day = str(datetime.datetime.strftime(video_cdate, "%d"))

        return formatted_date


    def rename_file(self, filename, media_type):
        if media_type == "photo":
            with open(filename, "rb") as file_stream:
                try:
                    tags = EXIF.process_file(file_stream)
                    datestr = str(tags["EXIF DateTimeDigitized"])
                    date_object = datetime.datetime.strptime(datestr,
                                                             "%Y:%m:%d %H:%M:%S")
                    formatted_date = datetime.datetime.strftime(date_object,
                                                                "%Y-%m-%d_%I-%M-%S_%p")

                    self.year = str(datetime.datetime.strftime(date_object, "%Y"))
                    self.month = str(datetime.datetime.strftime(date_object, "%m"))
                    self.day = str(datetime.datetime.strftime(date_object, "%d"))

                    camera_model = str(tags["Image Model"]).replace(" ", "_")

                    image_filename = os.path.split(filename)[1]
                    if image_filename.startswith("DSC"):
                        image_filename_base = os.path.splitext(image_filename)[0]
                        self.new_name = (camera_model + "_" + image_filename_base[4:] + "_" +
                                         formatted_date + ".jpg")
                    else:
                        self.new_name = camera_model + "_" + formatted_date + ".jpg"
                except KeyError:
                    sys.stderr.write("Key error reading EXIF tags")
                    self.log.error("Key error reading EXIF tags")
                    pass
        else:
            video_filename  = self.get_video_date(filename)
            video_root, video_ext = os.path.splitext(filename)
            self.new_name = video_filename + video_ext.lower()

        return self.new_name


    def create_directory(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)


    def delete_media_file(self, media_file):
        os.remove(os.path.join(self.src, media_file))


    def file_media_files(self):
        for f in self.fetch_files():
            if f.lower().endswith(".jpg"):
                if self.file_media_file(f, "photo"):
                    self.delete_media_file(f)
            elif f.lower().endswith((".mov", ".mp4")):
                if self.file_media_file(f, "video"):
                    self.delete_media_file(f)


    def file_media_file(self, media_file, media_type):
        try:
            self.renamed_media_file = self.rename_file(os.path.join(self.src, media_file), media_type)
            print self.renamed_media_file
            new_dir = os.path.join(self.dest, self.year, self.month, self.day)
            if not os.path.isfile(os.path.join(new_dir, self.renamed_media_file)):
                self.create_directory(new_dir)
                shutil.copyfile(os.path.join(self.src, media_file),
                                os.path.join(new_dir, self.renamed_media_file))
                self.log.info(media_file + " copied to " + os.path.join(new_dir, self.renamed_media_file))
                return 1
            else:
                # Quarantine dups
                shutil.copyfile(os.path.join(self.src, media_file),
                                os.path.join(self.dest, self.dups_dir, media_file))
                self.log.warning("DUPLICATE: " + media_file + " -- " + self.year + "/" +
                            self.month + "/" + self.day)
                return 1
        except Exception, err:
            sys.stderr.write("ERROR: %s\n" % str(err))
            self.log.error("ERROR: %s\n" % str(err))
            return 0
