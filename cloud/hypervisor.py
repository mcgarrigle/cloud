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
        self.conn = libvirt.open()
        self.instance = {}

    def domains(self):
        domains = {}
        for d in self.conn.listAllDomains():
            domain = Domain(d)
            domains[domain.name] = domain
        return domains

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
            'network':       list(guest.interfaces.values())
        }
        return instance

    def create_cloud(self, image):
        image.link(image.guest.os['path'])
        cdrom = Image(image.guest, "sr0")
        cdrom.cloud_init()
        return [image.disk(), cdrom.disk()]
            
    def create_clone(self, image):
        image.clone(image.guest.os['path'])
        return [image.disk()]
            
    def create_link(self, image):
        image.link(image.guest.os['path'])
        return [image.disk()]
            
    def create_install(self, guest):
        self.instance['location'] = guest.os['location']
        self.instance['extra-args'] = guest.args
        image.create()
        return [image.disk()]
    
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

    def create(self, guest):
        print(f"create {guest.name}")
        device = next(iter(guest.disks))
        size = guest.disks.pop(device)
        instance = self.create_instance(guest)
        instance['disk'] = self.create_boot_disk(guest, device, size)
        # create the rest of the disks
        for (device, size) in guest.disks.items():
            image = Image(guest, device, size)
            image.create()
            instance['disk'].append(image.disk())
        run('virt-install', instance)

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
