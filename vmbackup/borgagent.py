from subprocess import check_call,CalledProcessError,DEVNULL
from os import environ
import logging
from datetime import datetime

logger = logging.getLogger('vmbackup.borgagent')

# this is going to be run non-interactively, so make sure the backup runs
# focus is on resilience
borgenv = environ
borgenv['BORG_UNKNOWN_UNENCRYPTED_REPO_ACCESS_IS_OK'] = 'yes'

def borgcreate(repository, VMname, sourcepaths):
    backupname = repository + '::{hostname}_' + VMname + '_' + datetime.now().strftime('%Y.%j-%H.%M')
    commandline = []
    commandline.append('/usr/bin/borg')
    commandline.append('create')
    commandline.append('--read-special')
    commandline.append('--compression')
    commandline.append('lz4')
    commandline.append(backupname)
    commandline.extend(sourcepaths)
    logger.debug('trying to call borg, commandline: '+str(commandline))
    try:
        check_call(commandline, env=borgenv)
    except CalledProcessError as err:
            logger.error('error running borg: '+str(err))
            raise RuntimeError

def borgprune(VMname, repository):
    #prune can't deal with ::{hostname}
    pruneprefix = '{hostname}_' + VMname
    commandline = []
    commandline.append('/usr/bin/borg')
    commandline.append('prune')
    # one archive for every day of the week
    commandline.append('--keep-daily=7')
    # one for every week of the month
    commandline.append('--keep-weekly=4')
    # one for every month (-1 means all)
    commandline.append('--keep-monthly=-1')
    # for every year within the last 2 years
    commandline.append('--keep-yearly=2')
    commandline.append('--prefix='+pruneprefix)
    commandline.append(repository)
    logger.debug('trying to call borg, commandline: '+str(commandline))
    try:
        check_call(commandline, env=borgenv)
    except CalledProcessError as err:
        logger.error('error running borg: '+str(err))
        raise RuntimeError
