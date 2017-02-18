#!/usr/bin/env python3

from vHandyman import libvirttool, borgtool
from vHandyman.lvmtool import lvmtool


# workflow:
# get VM disks via libvirtmanager.diskfinder
# freeze VM via libvirtmanager.freeze
# create snapshots via lvmsnapshots.snapdisks
# thaw VM
# start borgbackup via 

def dumpVM(VMname):
    worker = libvirttool.libvirttool(VMname)
    disks = worker.diskfinder()
    lvmtool.snapdisks(disks)

VMs = ['sunman']
for VM in VMs:
    dumpVM(VM)

