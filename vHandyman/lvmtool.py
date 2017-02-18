import os
from subprocess import check_call,CalledProcessError,DEVNULL

# https://git.fedorahosted.org/cgit/lvm2.git/tree/python

class lvmtool:

    def snapdisks(disks):
        snapshots = []
        for disk in disks:
            lvname = os.path.basename(disk)
            vgname = os.path.split(os.path.dirname(disk))[1]
            snapname = lvname + '_snap' + str(os.getpid())
            try: check_call(['/sbin/lvm', 'lvcreate', '-s', '-L20g', '-n', snapname, os.path.join(vgname, lvname)])
            except CalledProcessError as err: print('could not create lvm snapshot:', err)
            snapshots.append(os.path.join(os.path.dirname(disk), snapname))
        return snapshots
