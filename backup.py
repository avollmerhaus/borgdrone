#!/usr/bin/env python3

from vmbackup.libvirtagent import libvirtagent
from vmbackup.lvmagent import snapdisks,removesnaps
from vmbackup.borgagent import borgcreate, borgprune
from os import remove
from sys import exit
from re import sub
import argparse
import logging
from datetime import datetime

def dump_and_prune(repository, VMname, shutdown):
    # remove trailing slashes, borg can't deal with /repo/::backupname
    repository = sub('/$', '', repository)
    backupbase = repository + '::{hostname}_' + VMname
    backupname = backupbase + datetime.now().strftime('%Y.%j-%H.%M')
    sourcepaths = []
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
    borgcreate(backupname=backupname, sourcepaths=sourcepaths)
    # clean up
    removesnaps(snaps)
    remove(domxmlfile)
    borgprune(backupbase=backupbase, repository=repository)

parser = argparse.ArgumentParser(description='Opinionated Backup for VMs or containers via Borg. At the moment we only support libvirt/kvm on LVM.\
Containers and flat files may be supported sometime in the future. Example: backup.py --repo ssh:///user@borg.example.com/backuphdd/borg --type kvm --sources myVM --shutdown')
parser.add_argument('--repo', metavar='repo', type=str, nargs=1, required=True, help='Target Borg repository. We automatically prefix backup names using client hostname, source name and timestamp.')
parser.add_argument('--type', metavar='type', type=str, nargs=1, required=True, choices=['lxc','kvm'], help='virtualization type, must be kvm or lxc')
parser.add_argument('--sources', metavar='sources', nargs='+', required=True, help='Names of KVM machines or containers to backup')
parser.add_argument('--shutdown', dest='shutdown', action='store_true', default=False, help='Shtudown sources for snapshotting (we try to freeze the guest FS via guest-agent otherwise)')
parser.add_argument('--debug', dest='debug', action='store_true', default=False, help='Activate debugging output')
args = parser.parse_args()

logger = logging.getLogger('vmbackup')
# without config, the logger gets a default config that throws everything below "warning" away
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
if args.debug:
    logger.setLevel(logging.DEBUG)
    logger.info('Loglevel set to DEBUG')
else:
    logger.setLevel(logging.INFO)

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
