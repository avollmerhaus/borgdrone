#!/usr/bin/env python3

from vmbackup import backup,vmManager

vmManager('foo')

#backup = btrfsFileBackup('/mnt/backuphdd/files')
#backup.rsync('/mnt/windows/daten')
#backup.rsync('/mnt/windows/Users')
#backup.rotateSnapshots('monthly')

