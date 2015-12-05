#!/usr/bin/env python3

from vmbackup import backup,vmManager

manager = vmManager('foo')
manager.shutdown()
manager.snapshot()
manager.start()

#backup = btrfsFileBackup('/mnt/backuphdd/files')
#backup.rsync('/mnt/windows/daten')
#backup.rsync('/mnt/windows/Users')
#backup.rotateSnapshots('monthly')

