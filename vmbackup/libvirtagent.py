import libvirt
from xml.etree import ElementTree as ET
from time import sleep
from tempfile import NamedTemporaryFile

# Todo:
# implement snapshot function that freezes, thaws and calls lvm or other snapshot providers automatically

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
        #VMxml = self.VM.XMLDesc(0)
        #XMLobj = ET.fromstring(VMxml)
        XMLobj = ET.fromstring(self.VM.XMLDesc(0))
        XMLsearchResults = XMLobj.findall('./devices/disk/source')
        # domain xml differs between LVM LVs and raw files
        for result in XMLsearchResults:
            for sourceType in ['dev', 'file']:
                disk = result.get(sourceType)
                if disk is not None:
                    disks.append(disk)
        return disks
    
    def shutdownACPI(self):
        # todo: make this private, only call from freeze
        # when some flag true and freeze fails
        while self.VM.state()[0] != libvirt.VIR_DOMAIN_SHUTOFF:
            self.VM.shutdown()
            sleep(5)

    def shutdownVM(self):
        try: self.VM.shutdownFlags(libvirt.VIR_DOMAIN_SHUTDOWN_GUEST_AGENT | libvirt.VIR_DOMAIN_SHUTDOWN_ACPI_POWER_BTN)
        except libvirt.libvirtError as err: print('unable to shutdown VM:', err)
        while self.VM.state()[0] != libvirt.VIR_DOMAIN_SHUTOFF:
            sleep(5)

    def startVM(self):
        try: self.VM.create()
        except libvirt.libvirtError as err: print('unable to start VM:', err)

    def fsFreeze(self):
        # it seems to be perfectly normal for snapshots of XFS devices to require recovery when created this way
        # see "man xfs_freeze", from google it seems a lot of people just use it and don't care.
        # tested for ntfs, seems to produce snapshots marked as "clean"
        self.VM.fsFreeze()

    def fsThaw(self):
        self.VM.fsThaw()
        
    def start(self):
        self.VM.create()
    
    def dumpXML(self):
        xmldump = NamedTemporaryFile(suffix='.xml', delete=False)
        xmldump.write(self.VM.XMLDesc(0).encode(encoding='utf-8'))
        xmldump.flush()
        return xmldump.name
