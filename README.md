vivian
======

vivian takes a directory of photos, reads the EXIF tags, and files the image 
based on the date taken. Some IPTC keywords (mostly date/time stuff) and the IPTC 
byline are also written to the file. This is some pretty messy code that was 
written years ago, but I'm working on cleaning it up.

Requirements
------------

* [EXIF.py](https://github.com/ianare/exif-py)
* [IPTC.py](https://pypi.python.org/pypi/IPTCInfo/)
