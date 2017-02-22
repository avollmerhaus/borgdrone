from subprocess import check_call,CalledProcessError,DEVNULL
from os import environ
from datetime import datetime

# this is going to be run non-interactively, so make sure the backup runs
# focus is on resilience
borgenv = environ
borgenv['BORG_UNKNOWN_UNENCRYPTED_REPO_ACCESS_IS_OK'] = 'yes'

def borgcreate(backupname, sourcepaths):
    backupname = backupname + datetime.now().strftime('%Y.%j-%H.%M')
    #print('backup', sourcepaths, 'to', backupname)
    commandline = []
    commandline.append('/usr/bin/borg')
    commandline.append('create')
    commandline.append('--read-special')
    commandline.append('--compression')
    commandline.append('lz4')
    commandline.append(backupname)
    commandline.extend(sourcepaths)
    try: check_call(commandline, env=borgenv)
    except CalledProcessError as err: print('error running borg', err)

def borgprune(backupname):
    commandline = []
    commandline.append('/usr/bin/borg')
    commandline.append('prune')
    commandline.append('--keep-daily=1')
    commandline.append('--keep-weekly=1')
    commandline.append('--keep-monthly=1')
    commandline.append('--prefix='+backupname)
    try: check_call(commandline, env=borgenv)
    except CalledProcessError as err: print('error running borg', err)
    print(commandline)

    #--keep-daily=1 --keep-weekly=1 --keep-monthly=1 --dry-run --prefix='vhost5_trac.tegelen.naskorsports.com' 
