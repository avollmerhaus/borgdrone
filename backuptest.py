#!/usr/bin/env python3

from vmbackup import backup,vmManager

manager = vmManager('devtest')

#manager.searchAndMount('/dev/vhost/devtest', 2)
manager.setDisk(sourceDisk='/dev/vhost/devtest2')
#manager.setupMappings()
#manager.shutdown()
#manager.snapshot()
#manager.start()

#backup = btrfsFileBackup('/mnt/backuphdd/files')
#backup.rsync('/mnt/windows/daten')
#backup.rsync('/mnt/windows/Users')
#backup.rotateSnapshots('monthly')

