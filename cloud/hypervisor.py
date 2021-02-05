import os
import sys
import tempfile
import shutil
import subprocess
import secrets
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
        self.instance = { 
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

    def create_cloud(self, image):
        image.link(image.guest.os['path'])
        cdrom = Image(image.guest, "sr0")
        cdrom.cloud_init()
        self.instance['disk'] = [image.disk(), cdrom.disk()]
            
    def create_clone(self, image):
        image.clone(image.guest.os['path'])
        self.instance['disk'] = [image.disk()]
            
    def create_link(self, image):
        image.link(image.guest.os['path'])
        self.instance['disk'] = [image.disk()]
            
    def create_install(self, guest):
        self.instance['location'] = guest.os['location']
        self.instance['extra-args'] = guest.args
            
    def create(self, guest):
        print(f"create {guest.name}")
        self.create_instance(guest)
        device = next(iter(guest.disks))
        size = guest.disks.pop(device)
        image = Image(guest, device, size)
        if guest.initialise == 'cloud':
            self.create_cloud(image)
        if guest.initialise == 'clone':
            self.create_clone(image)
        elif guest.initialise == 'link':
            self.create_link(image)
        elif guest.initialise == 'install':
            self.create_install(guest)
        else:
            sys.exit(f"initialise mode '{guest.initialise}' unknown")
        # create the rest of the disks
        for (device, size) in guest.disks.items():
            image = Image(guest, device, size)
            image.create()
            self.instance['disk'].append(image.disk())
        run('virt-install', self.instance)

    def start(self, guest):
        os.system(f"virsh start --domain {guest.name}")

    def stop(self, guest):
        os.system(f"virsh shutdown --domain {guest.name}")

    def __delete_file(self, path):
        if os.path.exists(path):
            os.remove(path)
        else:
            print("The file does not exist")

    def destroy(self, guest):
        os.system(f"virsh destroy --domain {guest.name}")
        os.system(f"virsh undefine --domain {guest.name}")
        for device in  guest.disks.keys():
            image = Image(guest, device)
            image.delete()
        if guest.initialise == 'cloud':
            cdrom = Image(guest, "sr0")
            cdrom.delete()
