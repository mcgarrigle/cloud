import os
import yaml

from cloud import *

# VIRT_ROOT = '/var/lib/libvirt/filesystems/'

class Guest:

    def __init__(self, name, defn):
        self.name       = name
        self.hostname   = defn.get('hostname', name)
        self.image      = defn.get('image')
        self.location   = defn.get('location')
        self.memory     = defn.get('memory', '1024')
        self.disks      = defn.get('disks', {'vda': '10G'})
        self.cores      = defn.get('cores', '1')
        self.interfaces = defn.get('interfaces', {'eth0': 'network=default'})
        self.state      = 'undefined'
        self.addr       = '-'
        self.args       = defn.get('args', '')
        if (self.image is None) and (self.location is None):
            raise ValueError("image and location are undefined")
        self.os = self.read_os_metadata()

    def read(self, path):
        with open(path, 'r') as f:
            return yaml.safe_load(f.read())

    def read_os_metadata(self):
        name = (self.image or self.location)
        return self.read(os.path.join(ROOT, "catalog", name + ".yaml"))

    def __str__(self):
        return f"{self.name} {self.state} {self.addr}"

    def dump(self):
        for a in vars(self):
            print (a, getattr(self, a))
