#!/usr/bin/env python3

from vHandyman.libvirttool import libvirttool
from vHandyman.lvmtool import lvmtool
from vHandyman.borgtool import borgtool


# workflow:
# get VM disks via libvirtmanager.diskfinder
# freeze VM via libvirtmanager.freeze
# create snapshots via lvmsnapshots.snapdisks
# thaw VM
# start borgbackup via 

def dumpVM(VMname):
    worker = libvirttool(VMname)
    disks = worker.diskfinder()
    lvmtool.snapdisks(disks)

VMs = ['sunman']
for VM in VMs:
    dumpVM(VM)

