import os
import sys
import tempfile
import shutil
import libvirt

from cloud import *
from cloud.domain     import Domain
from cloud.image      import Image
from cloud.disk       import Disk
from cloud.cloud_init import CloudInit
from cloud.process    import run

class Hypervisor:

    def __init__(self):
        # self.instance = {}
        self.conn = libvirt.open()
        libvirt.registerErrorHandler(f=Hypervisor.__libvirt_callback, ctx=None)
 
    # stop the client library from printing messages
    #
    # see: https://stackoverflow.com/questions/45541725/avoiding-console-prints-by-libvirt-qemu-python-apis

    @staticmethod
    def __libvirt_callback(userdata, err):
        pass

    def domains(self):
        return [ Domain(d) for d in self.conn.listAllDomains() ]

    def domain(self, name):
        try:
            return Domain(self.conn.lookupByName(name))
        except libvirt.libvirtError as e:
            return None

    def create_instance(self, guest):
        instance = { 
            'virt-type':     'kvm', 
            'import':        None,
            'noautoconsole': None,
            'graphics':      guest.graphics,
            'name':          guest.name,
            'memory':        guest.memory,
            'vcpus':         guest.cores, 
            'os-variant':    guest.os.variant,
            'disk':          [],
            'network':       [ i.to_virt_install() for i in guest.interfaces ]
        }
        return instance

    def create(self, guest):
        print(f"create {guest.name}")
        boot_device = next(iter(guest.disks))
        boot_size = guest.disks.pop(boot_device)
        boot       = Image(guest, boot_device, boot_size)
        cloud_init = CloudInit(guest)
        rest       = [ Disk(guest, device, size) for (device, size) in guest.disks.items() ]
        all_disks  = [ boot, cloud_init ] + rest
        for disk in all_disks:
            print(f"block device {disk.device} {disk.path}")
            disk.commit()
        self.instance = self.create_instance(guest)
        self.instance['disk'] = [ d.disk() for d  in all_disks ]
        run('virt-install', self.instance)

    def start(self, guest):
        os.system(f"virsh start --domain {guest.name}")

    def stop(self, guest):
        os.system(f"virsh shutdown --domain {guest.name}")

    def destroy(self, guest):
        os.system(f"virsh destroy --domain {guest.name}")
        os.system(f"virsh undefine --domain {guest.name}")
        if guest.initialise == 'cloud':
            guest.disks['sr0'] = 0
        for device in  guest.disks.keys():
            image = Image(guest, device)
            image.delete()
