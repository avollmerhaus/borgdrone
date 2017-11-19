import logging
import lxc

class lxcdrone:

    # https://www.stgraber.org/2014/02/05/lxc-1-0-scripting-with-the-api/
    # todo: diskfinder supports only lvm

    def __init__(self, container):
        self.logger = logging.getLogger('borgdrone.lxcdrone.'+container)
        self.logger.debug('working on %s', container)
        assert(container in lxc.list_containers()), 'Given container not found via LXC API'
        self.container = lxc.Container(container)

    def shutdown(self):
        self.container.shutdown(timeout=360)
        if not self.container.state == 'STOPPED':
            raise RuntimeError('Container refused to stop')
    
    def start(self):
        self.container.start()
    
    def snapshot(self):
        # really go through lxc api?
        raise NotImplementedError

    def freeze(self):
        self.container.freeze()

    def thaw(self):
        self.container.unfreeze()

    def diskfinder(self):
        disks = []
        disks.append(self.container.get_config_item('lxc.rootfs'))
        if not disks:
            self.logger.error('unable to find rootfs for container')
            raise RuntimeError

    def get_config(self):
        return self.container.config_file_name
