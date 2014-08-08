# vivian

vivian is a digital photo renamer and filer. Give it source and destination
directories and it will look for jpegs in source, pull out the date/time
digitized and camera model metadata from the EXIF headers, and rename the file
using the metadata, to a format of:

`CAMERA_MODEL_YYYY-MM-DD-hour-min-sec-AM/PM.jpg`

OR...

`iPhone_5_2014-08-06_6-07-18-PM.jpg`

After the rename, photos are filed by date to directories like so:

`./2014/08/05/`

vivian is currently running on a headless Raspberry Pi Model B hooked up to 2
1TB Samsung USB removable hard drives. vivian pushes to one drive, then a
```rsync``` cronjob syncs to the second drive daily at 5AM, as a backup.

## Integration with box.com

box.com offers free accounts just as do Dropbox and Bitcasa, among others. What
makes Box stand out is their support of the webDAV protocol, which is supported
on Linux. You can essentially create a drive that is in sync with your Box
account.

All of the following commands were done under Raspian, so YMMV.

First, create a directory for Box locally:

```$ sudo mkdir /media/box```

Install ```davfs2```, a Linux tool for connecting to WebDAV shares as though they
were local disks:

```sudo apt-get install davfs2```

Edit the file ```/etc/davfs2/secrets``` and add the next line at the bottom
of this file:

```https://dav.box.com/dav username password```

Finally, make mounting fully automatic. The Box cloud file system
will be mounted to ```/media/box``` when the system boots, which makes it
available at all times.

Replace the line you have added to the file /etc/fstab with the following line:

```https://dav.box.com/dav /media/box davfs rw,noexec,auto,user,async,_netdev,uid=pi,gid=pi 0 0```

### Testing the Box setup

On your phone or tablet, install the Box app for Android or iOS and login with
your free account. Push some photos to the account.

Back on the Pi, list the contents of the ```/media/box``` directory:

```
$ ls /media/box
20140627_120714.jpg  20140628_122316.jpg  20140718_113022.jpg
20140628_104135.jpg  20140710_215935.jpg  20140802_105343.jpg
20140628_104211.jpg  20140714_203812.jpg  lost+found
20140628_104214.jpg  20140716_104404.jpg
```

You can also login to Box through their website, drag and drop photos from your
computer, and they will also show up in the webDAV mount.

## Wiring it all together for a full solution

So now we have:

### Hardware

1. One Rapsberry Pi Model B
2. One [Belkin powered USB hub](http://www.amazon.com/gp/product/B005A0B3FG/ref=oh_aui_detailpage_o09_s00?ie=UTF8&psc=1),
3. Two [Seagate 1TB drives](http://www.amazon.com/gp/product/B00H4XH5FY/ref=s9_simh_gw_p147_d0_i1?pf_rd_m=ATVPDKIKX0DER&pf_rd_s=center-2&pf_rd_r=199708C3PTPACMVR5ABF&pf_rd_t=101&pf_rd_p=1688200382&pf_rd_i=507846)
4. Our laptops, phones, tablets that we want to push photos from

### Software

1. Vivian running on the Pi
2. ```davfs2``` installed and running on the Pi
3. Our box.com account wired up to a local directory via ```davfs2```
4. Android/iOS apps on devices to push photos up to Box
5. Drag-n-drop access to box.com on laptop through box.com website

### Cron job

Finally, to make this fully automatic, we need to setup a cron job on the Pi to
run vivian every N minutes.

I learned the hard way that editing the crontab in vim isn't a good idea - the
changes don't take (I'm probably doing something wrong). So on the Pi, run:

```$ crontab -e```

This opens up your crontab in nano. Add the following line:

```*/30 * * * * /path/to/run_vivian.py```

The above command executes the Python script ```run_vivian.py``` every 30 minutes
on the half hour.

Be sure to make ```run_vivian.py``` executable:

```$ chmod +x run_vivian.py```

Make sure the shebang in ```run_vivian.py``` is correct for your system. On my
Pi it is:

```#!/usr/bin/python```

## Creating mounts for 1TB backup drives

The following is how to mount the 1TB drives on the Pi.

Get a list of all drives:

```$ sudo fdisk -l```

My disks ended up being ```sda1``` and ```sdc1```

Make directories for the mounts we about to create:

```
$ sudo mkdir /media/bu-1
$ sudo mkdir /media/bu-2
$ sudo mkdir /media/bu-1/share
$ sudo mkdir /media/bu-2/share
```

Mount the drives to the directores just created:

```
$ pi@raspberrypi ~ $ sudo mount -t auto /dev/sda1 /media/bu-1
$ pi@raspberrypi ~ $ sudo mount -t auto /dev/sdc1 /media/bu-2
```

Install Samba

```sudo apt-get install samba samba-common-bin```

Backup Samba config file:

```sudo cp /etc/samba/smb.conf /etc/samba/smb.conf.old```

Edit the samba config file to add in our drive

```$ sudo vim /etc/samba/smb.conf```

Add this:

```
# ======================== bu1 HDD ==========================#
[backup-1]
comment = Backup folder
path = /media/bu-1/share
valid users = @users
force group = users
create mask = 0660
directory mask = 0771
read only = no
```

Bounce Samba:

```sudo /etc/init.d/samba restart```


Create backups user that can access the Pi's Samba shares:

```
$ sudo useradd backups -m -G users
$ sudo passwd backups
```

Enter your password

Add backups user to samba

```$ sudo smbpasswd -a backups```

Enter your password

### Connect to Pi on Mac

In Finder, go to Go > Connect to Server, enter:

```smb://10.0.1.50/backup-1/share```


### Automount the drives on Pi when Pi boots

```$ sudo vim /etc/fstab```

Add these lines:

```
/dev/sda1 /media/bu-1 auto noatime 0 0
/dev/sdc1 /media/bu-2 auto noatime 0 0
```

Now when the Pi boots, your drives get auto-mounted.


### Cron job to run rysnc daily at 5AM

So we have backup-1 as our main target directory for photo storage, backup-2 is
meant to mirror backup-1 for redundancy. Add a cron job to run ```rsync``` daily
at 5AM to push deltas over:

```$ vim crontab -e```

Add this line:

```0 5 * * * rsync -av --delete /media/bu-1/share /media/bu-2/share/```

## Requirements

* [EXIF.py](https://github.com/ianare/exif-py)
* ```davfs2``` (install through ```apt-get```

## Sources

I couldn't have done this without these great guides:

* [How to Turn a Raspberry Pi into a Low-Power Network Storage Device](http://www.howtogeek.com/139433/how-to-turn-a-raspberry-pi-into-a-low-power-network-storage-device/)
* [Mount box.com on your Raspberry Pi](http://www.sbprojects.com/projects/raspberrypi/webdav.php)