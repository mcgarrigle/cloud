import os

VIRT_ROOT = '/var/lib/libvirt/filesystems/'

class Guest:

    def __init__(self, name, defn):
        self.name     = name
        self.hostname = defn.get('hostname', name)
        self.image    = defn['image']
        self.memory   = defn.get('memory', '1024')
        self.disk     = defn.get('disk', '10G')
        self.cores    = defn.get('cores', '1')
        self.network  = defn.get('network', 'default')
        self.disk0    = os.path.join(VIRT_ROOT, self.name + '.qcow2')
        self.disk1    = os.path.join(VIRT_ROOT, self.name + '.iso')
        self.state    = 'undefined'
        self.addr     = '-'

    def __str__(self):
        return f"{guest.name} {guest.state} {guest.addr}"
