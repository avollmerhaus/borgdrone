Backup VMs or containers via Borg
===

Use Borgs `--read-special` to backup LVM snapshots and VM metadata (like libvirt XML description).

## Create Borg repo

`borg init --encryption=none /path/borg`

Hint:
If /path/ is on ZFS or BTRFS, disable filesystem compression.
Borg supports non-compressed repositorys, but we want data to be compressed when in transfer.

## 

