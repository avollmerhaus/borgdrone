#!/usr/bin/env python3

from vHandyman.libvirttool import libvirttool
from vHandyman.lvmtool import lvmtool
from vHandyman.borgtool import borgcreate
from os import remove

# todo: introduce some kind of switch to determine mode (freeze or shutdown)

def dumpVM(repo, VMname):
    backupname = repo + VMname
    sourcepaths = []

    virtworker = libvirttool(VMname)
    lvmworker = lvmtool()

    # find and snapshot all VM disks
    disks = virtworker.diskfinder()
    #virtworker.shutdownVM()
    virtworker.fsFreeze()
    snaps = lvmworker.snapdisks(disks)
    #worker.startVM()
    virtworker.fsThaw()
    sourcepaths.extend(snaps)
    
    # prepare VM xml definition to be included in backup
    domxmlfile = virtworker.dumpXML()
    sourcepaths.append(domxmlfile)

    # call borg to do the backup
    borgcreate(backupname=backupname, sourcepaths=sourcepaths)

    # clean up
    lvmworker.removesnaps()
    remove(domxmlfile)

VMs = ['trac.tegelen.naskorsports.com']
repo = 'ssh://locutus@cube.tegelen.naskorsports.com/zroot/borg/backups::{hostname}_'

for VM in VMs:
    dumpVM(repo=repo, VMname=VM)

