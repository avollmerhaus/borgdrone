from subprocess import check_call,CalledProcessError,DEVNULL
from datetime import datetime

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
    try: check_call(commandline)
    except CalledProcessError as err: print('error running borg', err)

