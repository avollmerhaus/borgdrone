#!/usr/bin/env python3.5

from borgdrone.libvirtdrone import libvirtdrone
from borgdrone.lxcdrone import lxcdrone
from borgdrone.lvmdrone import snapdisks,removesnaps
from borgdrone.borgdrone import borgcreate, borgprune
from os import remove
from re import sub
from logging.handlers import SysLogHandler
import argparse
import sys
import logging

def vm_dump_and_prune(repository, VMname, shutdown):
    # remove trailing slashes, borg can't deal with /repo/::backupname
    repository = sub('/$', '', repository)
    sourcepaths = []
    snaps = []
    domxmlfile = None

    try:
        virtualmachine = libvirtdrone(VMname)
        # find and snapshot all VM disks, shutting down or freezing VMs for the action
        disks = virtualmachine.diskfinder()
        if shutdown:
            virtualmachine.shutdownVM(timeout=1800)
        else:
            virtualmachine.fsFreeze()
        snaps = snapdisks(disks)
        sourcepaths.extend(snaps)
        # prepare VM xml definition to be included in backup
        domxmlfile = virtualmachine.dumpXML()
        sourcepaths.append(domxmlfile)
        # call borg to do the backup
        borgcreate(source_name=VMname, repository=repository, sourcepaths=sourcepaths)
    finally:
        if virtualmachine:
            try:
                if shutdown:
                    virtualmachine.startVM()
                else:
                    virtualmachine.fsThaw()
                # clean up
                if snaps:
                    removesnaps(snaps)
                if domxmlfile:
                    remove(domxmlfile)
            except Exception:
                logger.exception('failed cleanup or thaw/start VM')
        borgprune(source_name=VMname, repository=repository)

def container_dump_and_prune(repository, containername):

    repository = sub('/$', '', repository)
    sourcepaths = []
    snaps = []
    disks = []

    try:
        container = lxcdrone(containername)
        disks = container.diskfinder()
        container.freeze()
        snaps = snapdisks(disks)
        container.thaw()
        sourcepaths.extend(snaps)
        sourcepaths.append(container.get_config)
        borgcreate(source_name=containername, repository=repository, sourcepaths=sourcepaths)
    finally:
        container.thaw()
        if snaps:
            removesnaps(snaps)
        borgprune(source_name=containername, repository=repository)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Opinionated wrapper to backup VMs or containers via Borg. At the moment we only support libvirt/kvm on LVM.\
    Containers and flat files may be supported sometime in the future. Example: backup.py --repo ssh:///user@borg.example.com/backuphdd/borg --type kvm --sources myVM --shutdown')
    parser.add_argument('--repo', metavar='repo', type=str, nargs=1, required=True, help='Target Borg repository. We automatically prefix backup names using client hostname, source name and timestamp.')
    parser.add_argument('--type', metavar='type', type=str, nargs=1, required=True, choices=['lxc','kvm'], help='virtualization type, must be kvm or lxc')
    parser.add_argument('--sources', metavar='sources', nargs='+', required=True, help='Names of KVM machines or containers to backup')
    parser.add_argument('--shutdown', dest='shutdown', action='store_true', default=False, help='Shtudown sources for snapshotting (we try to freeze the guest FS via guest-agent otherwise)')
    parser.add_argument('--debug', dest='debug', action='store_true', default=False, help='Activate debugging output')
    parser.add_argument('--syslog', dest='syslog', action='store_true', default=False, help='Send logs to syslog')
    args = parser.parse_args()

    logger = logging.getLogger('borgdrone')
    logchannel = logging.StreamHandler(sys.stdout)
    logchannel.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(logchannel)

    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.info('Loglevel set to DEBUG')
    else:
        logger.setLevel(logging.INFO)

    if args.syslog:
        logchannel2 = SysLogHandler(address='/dev/log')
        # i'm not sure why it has to be exactly this format, SysLog seems to be picky
        logchannel2.setFormatter(logging.Formatter('%(asctime)s borgdrone: %(message)s'))
        logger.addHandler(logchannel2)

    exitcode = 3
    failedSources = []
    try:
        if args.type[0] == 'lxc':
            if args.shutdown:
                raise NotImplementedError
            for source in args.sources:
                try:
                    container_dump_and_prune(repository=args.repo[0], containername=source)
                except RuntimeError:
                    logger.error('Backup or cleanup failed for container: '+source)
                    failedSources.append(source)
            if failedSources:
                logger.info('these sources failed: '+str(failedSources))
            else:
                logger.info('all sources backed up successfully')
        if args.type[0] == 'kvm':
            for source in args.sources:
                logger.debug('args say: repo: '+args.repo[0]+' source: '+source)
                try:
                    vm_dump_and_prune(repository=args.repo[0], VMname=source, shutdown=args.shutdown)
                except RuntimeError:
                    logger.error('Backup or cleanup failed for VM: '+source)
                    failedSources.append(source)
        if failedSources:
            logger.info('these sources failed: %s', str(failedSources))
            exitcode = 1
        else:
            logger.info('all sources backed up successfully')
            exitcode = 0
    except Exception as err:
        logger.exception('something went wrong, quit.')
        exitcode = 2
    finally:
        logging.shutdown()
        sys.exit(exitcode)

