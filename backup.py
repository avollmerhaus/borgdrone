#!/usr/bin/env python3

from vmbackup.libvirtagent import libvirtagent
from vmbackup.lvmagent import snapdisks,removesnaps
from vmbackup.borgagent import borgcreate
from os import remove
from sys import exit
from re import sub
import argparse

def dumpVM(repo, VMname):
    backupname = repo + VMname
    sourcepaths = []

    virtdrone = libvirtagent(VMname)

    # find and snapshot all VM disks
    disks = virtdrone.diskfinder()
    #virtdrone.shutdownVM()
    virtdrone.fsFreeze()
    snaps = snapdisks(disks)
    #drone.startVM()
    virtdrone.fsThaw()
    sourcepaths.extend(snaps)

    # prepare VM xml definition to be included in backup
    domxmlfile = virtdrone.dumpXML()
    sourcepaths.append(domxmlfile)

    # call borg to do the backup
    #borgcreate(backupname=backupname, sourcepaths=sourcepaths)

    # clean up
    removesnaps()
    remove(domxmlfile)

#VMs = ['trac.tegelen.naskorsports.com']
#repo = 'ssh://locutus@cube.tegelen.naskorsports.com/zroot/borg/backups::{hostname}_'

# todo: introduce some kind of switch to determine mode (freeze or shutdown)
parser = argparse.ArgumentParser(description='Opinionated Backup for VMs or containers via Borg. At the moment we only support libvirt/kvm on LVM. Containers and flat files may be supported sometime in the future')
parser.add_argument('--repo', metavar='repo', type=str, nargs=1, help='Target Borg repository. We automatically prefix backup names using client hostname, source name and timestamp.', required=True)
parser.add_argument('--type', metavar='type', type=str, nargs=1, help='virtualization type, must be kvm or lxc', required=True, choices=['lxc','kvm'])
parser.add_argument('--sources', metavar='sources', nargs='+', help='Names of KVM machines or containers to backup', required=True)
args = parser.parse_args()

if args.type[0] == 'lxc':
    exit('not implemented yet')
elif args.type[0] == 'kvm':
    # remove trailing slashes, add hostname to repository
    repo = sub('/$', '', args.repo[0])
    repo = repo + '::{hostname}_'
    for source in args.sources:
        dumpVM(args.repo[0], VM)
        #print(repo, source)
