#!/usr/bin/env python3

import sys
import os
from subprocess import check_call,CalledProcessError,DEVNULL
import datetime
import re
import libvirt
from xml.etree import ElementTree as ET
from time import sleep

class backup:

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
        except CalledProcessError: print('There was some error removing the snapshot, assuming it does not yet exist')
        check_call(['/sbin/btrfs', 'subvolume', 'snapshot', '-r', self.absoluteTargetVolumePath, absoluteSnapshotPath])

class vmManager:
    
    def __init__(self, VM):
        print('Working on virtual maschine '+VM)
        conn = libvirt.open("qemu:///system")
        self.VM = conn.lookupByName(VM)

        # get VM disks
        VMxmlRoot = ET.fromstring(self.VM.XMLDesc(0))
        XMLsearchResults = VMxmlRoot.findall('./devices/disk/source')
        ## XMLsearchResult.items()

        for result in XMLsearchResults:
            #disk = result.get('dev')
            disk = result.get('file')
            print(disk)

        #self.VMdisk = XMLsearchResult.get('dev')
        #print(self.VMdisk)
        
        #try: self.VM = conn.lookupByName(VM)
        #except libvirt.libvirtError: print('Given VM does not exist or libvirt not running')

    def shutdown(self):
        while self.VM.state()[0] != libvirt.VIR_DOMAIN_SHUTOFF:
            self.VM.shutdown()
            sleep(5)

    def start(self):
        self.VM.create()

    def snapshot(self):
        self.mount()
        print('dummy')

    def mount(self):
        #check_call(['/sbin/kpartx', '-s', '-a', self.VMdisk])
        print('dummy')

    #def __del__(self):
        # remove device mapper mappings
        #check_call([''

