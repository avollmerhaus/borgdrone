Backup VMs or containers via Borg
===

A little wrapper using borgbackup/borg with `--read-special` to backup LVM snapshots and VM metadata (like libvirt XML description) to a repository.

Libvirt-based VMs can be shut down while taking the lvm snapshot or, when the guest agent is available, frozen for a brief moment (filesystem freeze).
Freezing is the default.

We DO want backups, so when in doubt, backup anyway (BORG_UNKNOWN_UNENCRYPTED_REPO_ACCESS_IS_OK=yes).

Comes with a hardcoded retention policy and does automatic pruning.
Supports logging to syslog.

## Create Borg repo

`borg init --encryption=whatever /path/borg`

Hint:
If /path/ is on ZFS or BTRFS, disable filesystem compression.
Borg supports non-compressed repositorys, but we want data to be compressed when in transfer.

## Schedule backup runs via cron
`borgdrone.py --syslog --repo ssh://locutus@cube.example.com/borg/backups --type kvm --sources vm1 vm2 vmN`
