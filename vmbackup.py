#!/usr/bin/env python3

import sys
import os
from subprocess import check_call,CalledProcessError,DEVNULL
import datetime
import re
import libvirt

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
        print(VM)


#backup = btrfsFileBackup('/mnt/backuphdd/files')
#backup.rsync('/mnt/windows/daten')
#backup.rsync('/mnt/windows/Users')
#backup.rotateSnapshots('monthly')

myvm = vmManager(''
