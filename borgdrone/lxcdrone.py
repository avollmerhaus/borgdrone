import lxc

class lxcdrone:

    # https://www.stgraber.org/2014/02/05/lxc-1-0-scripting-with-the-api/

    def __init__(self, container):
        raise NotImplementedError
        assert(container in lxc.list_containers()), 'Given container not found via LXC API'
        self.container = lxc.Container(container)

    def shutdown(self):
        raise NotImplementedError
        self.container.shutdown(timeout=360)
        assert(self.container.state == 'STOPPED'), 'Container refused to stop'
    
    def start(self):
        raise NotImplementedError
        self.container.start()
    
    def snapshot(self):
        # really go through lxc api?
        raise NotImplementedError

    def copyConfig(self):
        raise NotImplementedError
