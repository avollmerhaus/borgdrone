import libvirt
from xml.etree import ElementTree as ET
from time import sleep
from tempfile import NamedTemporaryFile
import logging

# Todo:
# implement snapshot function that freezes, thaws and calls lvm or other snapshot providers automatically

class libvirtdrone:

    def __init__(self, VMname):
        # loggers are hierachical using foo.bar notation
        self.logger = logging.getLogger('borgdrone.libvirtdrone.'+VMname)
        self.logger.info('Working on virtual maschine '+VMname)
        libvirt.registerErrorHandler(f=self._libvirt_silence_error, ctx=None)
        try:
            conn = libvirt.open("qemu:///system")
            self.VM = conn.lookupByName(VMname)
        except libvirt.libvirtError as err:
            self.logger.error('failed to initialize libvirt connection, '+str(err))
            raise RuntimeError
        self.logger.debug('connected to libvirtd and selected VM')

    def _libvirt_silence_error(self, err):
        # Don't log libvirt errors: global error handler will do that
        if err[3] != libvirt.VIR_ERR_ERROR:
            self.logger.warn('Non-error from libvirt: ' + err[2])

    def diskfinder(self):
        # return all disk backend paths contained within VM xml
        disks = []
        XMLobj = ET.fromstring(self.VM.XMLDesc(0))
        XMLsearchResults = XMLobj.findall('./devices/disk/source')
        # domain xml differs between LVM LVs and raw files
        for result in XMLsearchResults:
            for sourceType in ['dev', 'file']:
                disk = result.get(sourceType)
                if disk is not None:
                    disks.append(disk)
        if not disks:
            self.logger.error('found no virtual disks for machine')
            raise RuntimeError
        else:
            self.logger.debug('libvirtdrone found virtual disk sources: '+str(disks))
            return disks

    def shutdownVM(self, timeout):
        # todo: make this private, only call from freeze
        # when some flag true and freeze fails
        
        if not self.VM.state()[0] == libvirt.VIR_DOMAIN_SHUTOFF:
            try:
                self.VM.shutdownFlags(libvirt.VIR_DOMAIN_SHUTDOWN_GUEST_AGENT | libvirt.VIR_DOMAIN_SHUTDOWN_ACPI_POWER_BTN)
            except libvirt.libvirtError as err:
                self.logger.error('libvirt unable to shutdown VM:'+str(err))
                raise RuntimeError
            else:
                while self.VM.state()[0] != libvirt.VIR_DOMAIN_SHUTOFF:
                    timeout -= 1
                    sleep(1)
                    if timeout is 0:
                        self.logger.error('timeout while waiting to shutdown VM')
                        raise RuntimeError
                        break

    def startVM(self):
        try:
            self.VM.create()
            self.logger.debug('VM started')
        except libvirt.libvirtError as err:
            self.logger.error('failed to start VM'+str(err))
            raise RuntimeError

    def fsFreeze(self):
        # it seems to be perfectly normal for snapshots of XFS devices to require recovery when created this way
        # see "man xfs_freeze", from google it seems a lot of people just use it and don't care.
        # tested for ntfs, seems to produce snapshots marked as "clean"
        try:
            self.logger.debug('freezing FS...')
            self.VM.fsFreeze()
        except libvirt.libvirtError as err:
            self.logger.error('failed to freeze FS '+str(err))
            raise RuntimeError
        # catch specific qemu agent fail here

    def fsThaw(self):
        try:
            self.logger.debug('thawing FS...')
            self.VM.fsThaw()
        except libvirt.libvirtError as err:
            self.logger.error('failed to thaw FS'+str(err))
            raise RuntimeError

    def dumpXML(self):
        self.logger.debug('writing VM XML file')
        xmldump = NamedTemporaryFile(suffix='.xml', delete=False)
        xmldump.write(self.VM.XMLDesc(0).encode(encoding='utf-8'))
        xmldump.flush()
        self.logger.debug('wrote VM XML file to'+xmldump.name)
        return xmldump.name
