import os, sys, yaml

from types import SimpleNamespace

from cloud import *
from cloud.interface import Interface

class Guest:

    def __init__(self, name, defn):
        os_name = defn.get('os') or sys.exit("os is unset")
        self.name       = name
        self.hostname   = defn.get('hostname', name)
        self.initialise = defn.get('initialise', defn.get('initialize', 'clone'))
        self.memory     = defn.get('memory', '1024')
        self.disks      = defn.get('disks', {'vda': '10G'})
        self.cores      = defn.get('cores', '1')
        self.graphics   = defn.get('graphics', 'none')
        self.args       = defn.get('args', '')
        self.os         = self.read_os_metadata(os_name)
        self.state      = 'undefined'
        if self.initialise == 'copy':
            self.initialise = 'clone'
        interfaces = defn.get('interfaces', {'eth0': {'connection': 'network=default'}})
        self.interfaces = [ Interface(n, d) for (n, d) in interfaces.items() ]
        self.nameserver = defn.get('nameserver', {})

        # mac and addr refer to the first interface only
        
        self.mac  = None
        if self.interfaces[0].bootproto == 'static':
            self.addr = str(self.interfaces[0].addr.ip)
        else:
            self.addr = None

    def read_os_metadata(self, name):
        path = os.path.join(ROOT, "catalog", name + ".yaml")
        with open(path, 'r') as f:
            metadata =  yaml.safe_load(f.read())
            return SimpleNamespace(**metadata)

    def __str__(self):
        return f"{self.name} {self.state} {self.addr}"

    def dump(self):
        for a in vars(self):
            print(a, getattr(self, a))
