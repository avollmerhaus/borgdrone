import os
from subprocess import check_call,CalledProcessError,DEVNULL
import logging

# Todo: use lvm via python bindings
# https://git.fedorahosted.org/cgit/lvm2.git/tree/python

logger = logging.getLogger('borgdrone.lvmdrone')

def snapdisks(disks):
    snapshots = []
    for disk in disks:
        lvname = os.path.basename(disk)
        vgname = os.path.split(os.path.dirname(disk))[1]
        snapname = lvname + '_snap' + str(os.getpid())
        command = ['/sbin/lvm', 'lvcreate', '-s', '-L20g', '-n', snapname, os.path.join(vgname, lvname)]
        logger.debug('calling '+str(command))
        try:
            check_call(command, stdout=DEVNULL)
        except CalledProcessError as err:
            logger.error('could not create lvm snapshot: '+str(err))
            raise RuntimeError
        snapshots.append(os.path.join(os.path.dirname(disk), snapname))
    logger.debug('lvmdrone created snapshots: '+str(snapshots))
    return snapshots

def removesnaps(snapshots):
    for snapname in snapshots:
        command = ['/sbin/lvm', 'lvremove', '-f', snapname]
        logger.debug('calling '+str(command))
        try:
            check_call(command, stdout=DEVNULL)
        except CalledProcessError as err:
            logger.error('could not remove lvm snapshot: '+str(err))
            raise RuntimeError
    logger.debug('lvmdrone removed snapshots: '+str(snapshots))
