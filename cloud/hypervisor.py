import os
import sys
import tempfile
import shutil
import libvirt

from cloud import *
from cloud.domain  import Domain
from cloud.image   import Image
from cloud.process import run

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
            'os-type':       guest.os['type'],
            'os-variant':    guest.os['variant'],
            'disk':          [],
            'network':       [ i.to_virt_install() for i in guest.interfaces ]
        }
        return instance

    def create_cloud(self, image):
        image.clone(image.guest.os['path'])
        cdrom = Image(image.guest, "sr0")
        cdrom.cloud_init()
        return [image, cdrom]
            
    def create_clone(self, image):
        image.clone(image.guest.os['path'])
        return [image]
            
    def create_link(self, image):
        image.link(image.guest.os['path'])
        return [image]
            
    def create_install(self, image):
        self.instance['location']   = image.guest.os['location']
        self.instance['extra-args'] = image.guest.args
        image.create()
        return [image]
    
    def create_boot_disk(self, guest, device, size):
        image = Image(guest, device, size)
        if guest.initialise == 'cloud':
            return self.create_cloud(image)
        elif guest.initialise == 'clone':
            return self.create_clone(image)
        elif guest.initialise == 'link':
            return self.create_link(image)
        elif guest.initialise == 'install':
            return self.create_install(image)
        else:
            sys.exit(f"initialise mode '{guest.initialise}' unknown")

    def create_blank_disk(self, guest, device, size):
        image = Image(guest, device, size)
        image.create()
        return image

    def create(self, guest):
        print(f"create {guest.name}")
        device = next(iter(guest.disks))
        size = guest.disks.pop(device)
        self.instance = self.create_instance(guest)
        boot = self.create_boot_disk(guest, device, size)
        rest = [ self.create_blank_disk(guest, device, size) for (device, size) in guest.disks.items() ]
        self.instance['disk'] = [ d.disk() for d  in (boot + rest) ]
        run('virt-install', self.instance)

    def start(self, guest):
        os.system(f"virsh start --domain {guest.name}")

    def stop(self, guest):
        os.system(f"virsh shutdown --domain {guest.name}")

    def destroy(self, guest):
        os.system(f"virsh destroy --domain {guest.name}")
        os.system(f"virsh undefine --domain {guest.name}")
        if guest.initialise == 'cloud':
            guest.disks["sr0"] = 0
        for device in  guest.disks.keys():
            image = Image(guest, device)
            image.delete()
