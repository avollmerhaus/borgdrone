#!/usr/bin/env python3

import sys
import os
import stat
from subprocess import check_call,CalledProcessError,DEVNULL
import datetime
import re
import libvirt
from xml.etree import ElementTree as ET
from time import sleep
import lxc

# overview:
# backup all disks of a VM to flat files, rotate flat-file storage using btrfsa
# use deduplication to remove duplicated data, sys-fs/duperemove or bedup (not in portage?)
# app-emulation/libguestfs - interesting?

# workflow:
# extract paths 
# stop VM
# take snapshots
# start VM
# dump VM config to backup
# rsync snapshot content over to backup btrfs volume
# rotate 

class dataManager:

    def __init__(self, btrfsvolume):
        self.absoluteTargetVolumePath = btrfsvolume
        assert(os.path.isdir(self.absoluteTargetVolumePath)), 'BTRFS subvolume '+self.absoluteTargetVolumePath+' not found'

    def rsync(self, absoluteSourcePath):
        # sanity checks
        assert(os.path.isdir(absoluteSourcePath)), 'Source directory '+absoluteSourcePath+' not found'
        assert not(re.match('.*/$', absoluteSourcePath)), 'Source path contains a trailing slash, that would cause rsync to dump the subfolders into the backup target'

        # final sanity check, check whether source, target and root are actually different filesystems
        # we do this via inodes because checking for mount points is moot when copying subfolders of subfolders to subvolumes
        ## TODO; relevant: check whether os.lstat(absoluteSourcePath).st_dev and similar for root and target are all different
        
        # all fine, now we can run rsync
        print('Copying '+absoluteSourcePath+' to '+self.absoluteTargetVolumePath)
        check_call(['/usr/bin/rsync', '--inplace', '--recursive', '--delete', absoluteSourcePath, self.absoluteTargetVolumePath])

    def rotateSnapshots(self, interval):
        #assert(interval in ['monthly', 'daily']), 'please select monthly or daily for argv[1]'
        SnapshotDate = datetime.datetime.now()
        if(interval == 'monthly'):
            absoluteSnapshotPath = self.absoluteTargetVolumePath+'_'+SnapshotDate.strftime('%B')
        elif(interval == 'daily'):
            absoluteSnapshotPath = self.absoluteTargetVolumePath+'_'+SnapshotDate.strftime('%A')
        else:
            raise ValueError('please select monthly or daily for argv[1]')

        try: check_call(['/sbin/btrfs', 'subvolume', 'delete', absoluteSnapshotPath], stderr=DEVNULL)
        except CalledProcessError: print('There was some error removing the snapshot, assuming it just did not yet exist')
        check_call(['/sbin/btrfs', 'subvolume', 'snapshot', '-r', self.absoluteTargetVolumePath, absoluteSnapshotPath])

    def cloneBinary(self, disks):
        raise NotImplementedError
        # don't check whether disk is LV or not
        # we can clone anyway, if that is what the user wants
        for disk in disks:
            targetFile = disk.split('/')[-1]
            #with

class libvirtManager:
    
    def __init__(self, VM):
        print('Working on virtual maschine '+VM)
        conn = libvirt.open("qemu:///system")
        self.VM = conn.lookupByName(VM)
        self.VMxml = self.VM.XMLDesc(0)

    def diskFinder(self):
        # return all disk paths contained within VM xml
        disks = []

        XMLobj = ET.fromstring(self.VMxml)
        XMLsearchResults = XMLobj.findall('./devices/disk/source')
       
        # domain xml differs between LVM LVs and raw files
        for result in XMLsearchResults:
            for sourceType in ['dev', 'file']:
                disk = result.get(sourceType)
                if disk is not None:
                    disks.append(disk)
        return disks


    def shutdown(self):
        while self.VM.state()[0] != libvirt.VIR_DOMAIN_SHUTOFF:
            self.VM.shutdown()
            sleep(5)

    def start(self):
        self.VM.create()

    def snapshot(self):
        # at the moment we only support LVM. BTRFS gives abysmal performance with COW, and without COW it's useless
        snapshots = []
        for disk in self.diskFinder():
            assert(stat.S_ISBLK(os.stat('/dev/tty').st_mode)), 'disk ' + disk + ' is not a blockdevice, unsupported'
            snapshotname = disk + '_snap'
            # actually do the snapshot!
            snapshots.append(snapshotname)
        return snapshots


        #item['filename'] = item['URL'].split('/')[-1]
    
    def dumpXML(self):
        raise NotImplementedError
        #with

class lxcManager:

    # https://www.stgraber.org/2014/02/05/lxc-1-0-scripting-with-the-api/

    def __init__(self, container):
        raise NotImplementedError
        assert(container in lxc.list_containers()), 'Given container not found via LXC API'
        self.container = lxc.Container(container)

    def shutdown(self):
        raise NotImplementedError
        self.container.shutdown(timeout=360)
        assert(self.container.state == 'STOPPED'), 'Container refused to stop'
    
    def start(self):
        raise NotImplementedError
        self.container.start()
    
    def snapshot(self):
        raise NotImplementedError

    def copyConfig(self):
        raise NotImplementedError
