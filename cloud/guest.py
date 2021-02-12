import os, sys, yaml

from cloud import *

# VIRT_ROOT = '/var/lib/libvirt/filesystems/'

class Guest:

    def __init__(self, name, defn):
        os_name = defn.get('os')
        if os_name is None:
            sys.exit("os is unset")
        self.name       = name
        self.hostname   = defn.get('hostname', name)
        self.initialise = defn.get('initialise')
        if self.initialise is None:
            self.initialise = defn.get('initialize', 'clone')
        self.memory     = defn.get('memory', '1024')
        self.disks      = defn.get('disks', {'vda': '10G'})
        self.cores      = defn.get('cores', '1')
        self.interfaces = defn.get('interfaces', {'eth0': 'network=default'})
        self.graphics   = defn.get('graphics', 'none')
        self.args       = defn.get('args', '')
        self.os         = self.read_os_metadata(os_name)
        self.state      = 'undefined'
        self.addr       = '-'
        if self.initialise == 'copy':
            self.initialise = 'clone'

    def read_os_metadata(self, name):
        path = os.path.join(ROOT, "catalog", name + ".yaml")
        with open(path, 'r') as f:
            return yaml.safe_load(f.read())

    def __str__(self):
        return f"{self.name} {self.state} {self.addr}"

    def dump(self):
        for a in vars(self):
            print(a, getattr(self, a))
