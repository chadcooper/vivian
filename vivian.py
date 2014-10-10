import sys
import EXIF
import os
import shutil
import logging
import logging.handlers


class Logger(object):
    def __init__(self, dest):
        self.log_filename = os.path.join(dest, "vivian.log")


    def create_logger(self):
        log = logging.getLogger("vivi_logger")
        log.setLevel(logging.DEBUG)
        handler = logging.handlers.RotatingFileHandler(self.log_filename,
                                                       maxBytes=20000,
                                                       backupCount=5)
        frmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
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


    def rename_file(self, filename):
        with open(filename, "rb") as file_stream:
            try:
                tags = EXIF.process_file(file_stream)
                datestr = str(tags["EXIF DateTimeDigitized"])
                camera_model = str(tags["Image Model"]).replace(" ", "_")

                datestr = datestr.split(" ")
                date = datestr[0]
                time = datestr[1]

                self.year = date.split(":")[0]

                if len(date.split(":")[1]) < 2:
                    self.month = str("0") + str(date.split(":")[1])
                else:
                    self.month = str(date.split(":")[1])

                if len(date.split(":")[2]) < 2:
                    self.day = str("0") + str(date.split(":")[2])
                else:
                    self.day = str(date.split(":")[2])

                if int(time.split(":")[0]) < 13:
                    hour = str(time.split(":")[0])
                    am_pm = "AM"
                elif int(time.split(":")[0]) > 12:
                    hour = str((int(time.split(":")[0]) - 12))
                    am_pm = "PM"

                min = str(time.split(":")[1])
                sec = str(time.split(":")[2])

                self.new_name = (camera_model + "_" + self.year + "-" +
                            self.month + "-" + self.day + "_" + hour + "-" +
                            min + "-" + sec + "-" + am_pm + ".jpg")

                return self.new_name

            except KeyError:
                sys.stderr.write("Key error ")
                self.log.error("Key error ")
                pass


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
                self.file_media_file(f, "video")
                    #self.delete_media_file(f)


    def file_media_file(self, media_file, media_type):
        try:
            self.renamed_media_file = self.rename_file(os.path.join(self.src, media_file), media_type)
            print self.renamed_media_file
            new_dir = os.path.join(self.dest, media_type, self.year, self.month, self.day)
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
