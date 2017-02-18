class borgtool:

    from subprocess import check_call,CalledProcessError,DEVNULL
    
    def borgcreate(self, repo, sourcepaths):
        raise NotImplementedError
        commandline = []
        commandline.append('/usr/bin/borg')
        commandline.append('--read-special')
        commandline.append('--compression')
        commandline.append('lz4')
        commandline.append(repo)
        commandline.append(sourcepaths) #unpack this?
        try: check_command(commandline)
        except CalledProcessError as err: print('error running borg', err)

