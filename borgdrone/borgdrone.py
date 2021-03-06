from subprocess import check_call, CalledProcessError, DEVNULL
from os import environ
import logging
from datetime import datetime

# TODO: explore importing from borg (it's python as well)

logger = logging.getLogger('borgdrone.borgdrone')

# this is going to be run non-interactively, so make sure the backup runs
# focus is on resilience
borgenv = environ
borgenv['BORG_UNKNOWN_UNENCRYPTED_REPO_ACCESS_IS_OK'] = 'yes'
borgenv['BORG_RELOCATED_REPO_ACCESS_IS_OK'] = 'yes'


def borgcreate(repository, source_name, sourcepaths):
    backupname = repository + '::{hostname}_' + source_name + '_' + datetime.now().strftime('%Y.%j-%H.%M')
    commandline = []
    commandline.append('/usr/bin/borg')
    commandline.append('create')
    commandline.append('--read-special')
    commandline.append('--compression')
    commandline.append('lz4')
    commandline.append(backupname)
    commandline.extend(sourcepaths)
    logger.debug('trying to call borg, commandline: %s', str(commandline))
    try:
        check_call(commandline, env=borgenv)
    except CalledProcessError as err:
        logger.error('error running borg: %s', str(err))
        raise RuntimeError


def borgprune(source_name, repository):
    # prune can't deal with ::{hostname}
    pruneprefix = '{hostname}_' + source_name
    commandline = []
    commandline.append('/usr/bin/borg')
    commandline.append('prune')
    # one archive for every day for the last 2 weeks ...
    commandline.append('--keep-daily=14')
    # ... and for every month for the past year
    commandline.append('--keep-monthly=12')
    commandline.append('--prefix=' + pruneprefix)
    commandline.append(repository)
    logger.debug('trying to call borg, commandline: %s', str(commandline))
    try:
        check_call(commandline, env=borgenv)
    except CalledProcessError as err:
        logger.error('error running borg: %s', str(err))
        raise RuntimeError
