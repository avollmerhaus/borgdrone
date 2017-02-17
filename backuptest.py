#!/usr/bin/env python3

from vmtools import libvirttool, lvmtool, borgtool

# workflow:
# get VM disks via libvirtmanager.diskfinder
# freeze VM via libvirtmanager.freeze
# create snapshots via lvmsnapshots.snapdisks
# thaw VM
# start borgbackup via 

def dumpVM(VMname):
    handyman = libvirttool(VM)
    disks = handyman.diskfinder()
    print(disks)
    lvmtool.snapdisks(disks)
    
    

VMs = ['sunman']

for VM in VMs:
    dumpVM(VM)

