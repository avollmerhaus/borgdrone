#!/usr/bin/env python3

from vmbackup.libvirtagent import libvirtagent
from vmbackup.lvmagent import snapdisks,removesnaps
from vmbackup.borgagent import borgcreate, borgprune
from os import remove
from sys import stdout
from re import sub
from logging.handlers import SysLogHandler
import argparse
import logging

def dump_and_prune(repository, VMname, shutdown):
    # remove trailing slashes, borg can't deal with /repo/::backupname
    repository = sub('/$', '', repository)
    sourcepaths = []
    snaps = []
    domxmlfile = None

    try:
        virtdrone = libvirtagent(VMname)
        # find and snapshot all VM disks, shutting down or freezing VMs for the action
        disks = virtdrone.diskfinder()
        if shutdown:
            virtdrone.shutdownVM(timeout=1800)
        else:
            virtdrone.fsFreeze()
        snaps = snapdisks(disks)
        if shutdown:
            virtdrone.startVM()
        else:
            virtdrone.fsThaw()
        sourcepaths.extend(snaps)
        # prepare VM xml definition to be included in backup
        domxmlfile = virtdrone.dumpXML()
        sourcepaths.append(domxmlfile)
        # call borg to do the backup
        borgcreate(VMname=VMname, repository=repository, sourcepaths=sourcepaths)
    finally:
        # clean up
        if snaps:
            removesnaps(snaps)
        if domxmlfile:
            remove(domxmlfile)
        borgprune(VMname=VMname, repository=repository)

parser = argparse.ArgumentParser(description='Opinionated wrapper to backup VMs or containers via Borg. At the moment we only support libvirt/kvm on LVM.\
Containers and flat files may be supported sometime in the future. Example: backup.py --repo ssh:///user@borg.example.com/backuphdd/borg --type kvm --sources myVM --shutdown')
parser.add_argument('--repo', metavar='repo', type=str, nargs=1, required=True, help='Target Borg repository. We automatically prefix backup names using client hostname, source name and timestamp.')
parser.add_argument('--type', metavar='type', type=str, nargs=1, required=True, choices=['lxc','kvm'], help='virtualization type, must be kvm or lxc')
parser.add_argument('--sources', metavar='sources', nargs='+', required=True, help='Names of KVM machines or containers to backup')
parser.add_argument('--shutdown', dest='shutdown', action='store_true', default=False, help='Shtudown sources for snapshotting (we try to freeze the guest FS via guest-agent otherwise)')
parser.add_argument('--debug', dest='debug', action='store_true', default=False, help='Activate debugging output')
parser.add_argument('--syslog', dest='syslog', action='store_true', default=False, help='Send logs to syslog')
args = parser.parse_args()

logger = logging.getLogger('vmbackup')
logchannel = logging.StreamHandler(stdout)
logchannel.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(logchannel)

if args.debug:
    logger.setLevel(logging.DEBUG)
    logger.info('Loglevel set to DEBUG')
else:
    logger.setLevel(logging.INFO)

if args.syslog:
    logchannel2 = SysLogHandler(address='/dev/log')
    #logchannel2.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
    #logchannel2.setFormatter(logging.Formatter('%(message)s s%(message) s%(message) s%(message) s%(message)s'))
    logchannel2.setFormatter(logging.Formatter('%(asctime)s vmbackup: %(message)s'))
    #logchannel2.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(logchannel2)

failedSources = []
if args.type[0] == 'lxc':
    logger.warn('LXC is not implemented yet')
elif args.type[0] == 'kvm':
    for source in args.sources:
        logger.debug('args say: repo: '+args.repo[0]+' source: '+source)
        try:
            dump_and_prune(repository=args.repo[0], VMname=source, shutdown=args.shutdown)
        except RuntimeError:
            logger.error('Backup or cleanup failed for VM: '+source)
            failedSources.append(source)
    if failedSources:
        logger.info('these sources failed: '+str(failedSources))
    else:
        logger.info('all sources backed up successfully')
