Backup VMs or containers via Borg
===

# Disclaimer
Experimental version of rewrite mentioned here earlier.

A little wrapper using borgbackup/borg with `--read-special` to backup LVM snapshots and VM metadata (like libvirt XML description) to a repository.

Comes with a hardcoded retention policy and does automatic pruning.

## Create Borg repo

`borg init --encryption=whatever /path/borg`

Hint:
If /path/ is on ZFS or BTRFS, disable filesystem compression.
Borg supports non-compressed repositorys, but we want data to be compressed when in transfer.

## Schedule backup runs via cron
`borgdrone.py --syslog --repo ssh://locutus@cube.example.com/borg/backups --type kvm --sources vm1 vm2 vmN`
