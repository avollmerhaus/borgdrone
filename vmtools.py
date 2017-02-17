#!/usr/bin/env python3

import sys
import os
import stat
from subprocess import check_call,CalledProcessError,DEVNULL
import datetime
import re
import libvirt
from xml.etree import ElementTree as ET
from time import sleep
import lxc

# todo:
# split classes into files
# libvirtmanager should be able to consume lvmmanager itself
# enhance libvirt dumpxml so it actually dumps the xml so we can feed it to borg, see create temp file

class borgtool:

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
        
class lvmtool:
    
    #def snapdisks(self, disks):
    def snapdisks(disks):
        snapshots = []
        for disk in disks:
            lvname = os.path.basename(disk)
            vgname = os.path.split(os.path.dirname(disk))[1]
            snapname = lvname + '_snap' + str(os.getpid())
            try: check_call(['/sbin/lvm', 'lvcreate', '-s', '-L20g', '-n', snapname, os.path.join(vgname, lvname)])
            except CalledProcessError as err: print('could not create lvm snapshot:', err)
            snapshots.append(os.path.join(os.path.dirname(disk), snapname))
        return snapshots
            

class libvirttool:
    
    def __init__(self, VMname):
        print('Working on virtual maschine '+VMname)
        try:
            conn = libvirt.open("qemu:///system")
            self.VM = conn.lookupByName(VMname)
        except libvirt.libvirtError as err: print(VMname+':failed to initialize libvirt connection:', err)

    def diskfinder(self):
        # return all disk paths contained within VM xml
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

class lxctool:

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
        raise NotImplementedError

    def copyConfig(self):
        raise NotImplementedError
