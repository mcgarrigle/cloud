import os
import tempfile
import shutil
import subprocess
import secrets
import libvirt

from cloud import *
from cloud.domain import Domain
from cloud.image  import Image

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

    # take lists of lists or tuples and return flattened list

    def flatten(self, a):
        return [y for x in a for y in x]

    def parameter(self, s):
        return f"--{s}"

    def expand(self, k, g):
        tuples = [(self.parameter(k), v) for v in g]
        return self.flatten(tuples)

    def argv(self, args):
        singles = [ (self.parameter(k), str(v)) for (k, v) in args.items() if type(v) is str]
        groups = [ self.expand(k, v) for (k, v) in args.items() if type(v) is list]
        return self.flatten(singles) + self.flatten(groups)

    def create_instance(self, guest):
        self.instance = { 
            'virt-type':  'kvm', 
            'graphics':   'none' ,
            'name':       guest.name,
            'memory':     guest.memory,
            'vcpus':      guest.cores, 
            'os-type':    guest.os['type'],
            'os-variant': guest.os['variant'],
            'disk':      [],
            'network':   list(guest.interfaces.values())
        }

    def create_from_image(self, guest):
        (name, size) = next(iter(guest.disks.items()))
        image = Image(guest, name, size)
        image.clone(guest.os['path'])
        cdrom = Image(guest, "sr0")
        cdrom.cloud_init()
        self.instance['disk'] = [image.disk(), cdrom.disk()]
            
    def create_from_boot(self, guest):
        print("boot")
        self.instance['location'] = guest.os['location']
        self.instance['extra-args'] = guest.args
        for (name, size) in guest.disks.items():
            image = Image(guest, name, size)
            image.create()
            self.instance['disk'].append(image.disk())
            
    def create(self, guest):
        print(f"create {guest.name}")
        self.create_instance(guest)
        if guest.image:
            self.create_from_image(guest)
        else:
            self.create_from_boot(guest)
        print(self.instance)
        args = ["virt-install", "--import", "--noautoconsole"] + self.argv(self.instance)
        print(' '.join(args))
        subprocess.call(args)

    def delete_file(self, path):
        if os.path.exists(path):
            os.remove(path)
        else:
            print("The file does not exist")

    def destroy(self, guest):
        os.system(f"virsh destroy --domain {guest.name}")
        os.system(f"virsh undefine --domain {guest.name}")
        self.delete_file(guest.disk0)
        self.delete_file(guest.disk1)
