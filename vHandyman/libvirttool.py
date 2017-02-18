import libvirt
from xml.etree import ElementTree as ET
from time import sleep

class libvirttool:

    def __init__(self, VMname):
        print('Working on virtual maschine '+VMname)
        try:
            conn = libvirt.open("qemu:///system")
            self.VM = conn.lookupByName(VMname)
        except libvirtError as err: print(VMname+':failed to initialize libvirt connection:', err)

    def diskfinder(self):
        # return all disk backend paths contained within VM xml
        disks = []
        VMxml = self.VM.XMLDesc(0)
        XMLobj = ET.fromstring(VMxml)
        XMLsearchResults = XMLobj.findall('./devices/disk/source')
        # domain xml differs between LVM LVs and raw files
        for result in XMLsearchResults:
            for sourceType in ['dev', 'file']:
                disk = result.get(sourceType)
                if disk is not None:
                    disks.append(disk)
        return disks
    
    def shutdown(self):
        # todo: make this private, only call from freeze
        # when some flag true and freeze fails
        while self.VM.state()[0] != libvirt.VIR_DOMAIN_SHUTOFF:
            self.VM.shutdown()
            sleep(5)

    def freezeVM(self):
        self.VM.fsFreeze()

    def thawVM(self):
        self.VM.fsThaw()
        
    def start(self):
        self.VM.create()
    
    def dumpXML(self):
        raise NotImplementedError
        #with

