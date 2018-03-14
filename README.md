Backup VMs or containers via Borg
===

# Disclaimer
This Stuff is not safe to use without serious handholding.
For example, in its current state, it fails horribly when trying to backup a VM that has an iso image inserted into it's virtual DVD drive.
It needs a major rewrite.

A little wrapper using borgbackup/borg with `--read-special` to backup LVM snapshots and VM metadata (like libvirt XML description) to a repository.

This needs some work to be any good. It's not installable, fails to follow best practice
and can under certain conditions leave behind a mess.
LXC is not working and will probably only ever work when used with LVM as a backend.

Still useful as a quick and dirty hack though.

Libvirt-based VMs can be shut down while taking the lvm snapshot or, when the guest agent is available, frozen for a brief moment (filesystem freeze).
Freezing is the default.

We DO want backups, so when in doubt, backup anyway (BORG_UNKNOWN_UNENCRYPTED_REPO_ACCESS_IS_OK=yes).

Comes with a hardcoded retention policy and does automatic pruning.

## Create Borg repo

`borg init --encryption=whatever /path/borg`

Hint:
If /path/ is on ZFS or BTRFS, disable filesystem compression.
Borg supports non-compressed repositorys, but we want data to be compressed when in transfer.

## Schedule backup runs via cron
`borgdrone.py --syslog --repo ssh://locutus@cube.example.com/borg/backups --type kvm --sources vm1 vm2 vmN`
