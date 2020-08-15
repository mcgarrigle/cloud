import os, re, yaml
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

    def read(self, path):
        with open(path, 'r') as f:
            return yaml.safe_load(f.read())

    def write(self, path, data):
        with open(path, 'w') as f:
            f.write(yaml.dump(data))

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
        name = (guest.image or guest.location)
        self.config = self.read(os.path.join(ROOT, "catalog", name + ".yaml"))
        self.instance = { 
            'virt-type':  'kvm', 
            'graphics':   'none' ,
            'name':       guest.name,
            'memory':     guest.memory,
            'vcpus':      guest.cores, 
            'os-type':    self.config['type'],
            'os-variant': self.config['variant'],
            'disk':      [],
            'network':   list(guest.interfaces.values())
        }

    def read_os_metadata(self, guest):
        name = (guest.image or guest.location)
        return self.read(os.path.join(ROOT, "catalog", name + ".yaml"))

    def image_path(self, name, volume):
        return os.path.join(VIRT_ROOT, name + '_' + volume + '.qcow2')

    def clone_image(self, guest):
        path = os.path.join(VIRT_ROOT, guest.name + '.qcow2')
        image = self.read(os.path.join(ROOT, "catalog", guest.image + ".yaml"))
        os.system(f"qemu-img create -f qcow2 -b {image['path']} {guest.disk0} {guest.disk}")
        return image

    def create_cloud_init(self, guest):
        root = tempfile.TemporaryDirectory()
        metapath = os.path.join(root.name, "meta-data")
        userpath = os.path.join(root.name, "user-data")
        metadata = {
            'instance-id': secrets.token_hex(15),
            'local-hostname': guest.hostname
        }
        self.write(metapath, metadata)
        local = os.path.join(os.environ['HOME'], ".cloud_config")
        if os.path.isfile(local):
            path = local
        else:
            path = os.path.join(ROOT, "metadata", "user-data")
        shutil.copy(path, userpath)
        print(path)
        os.system(f"genisoimage " 
            f"-joliet " 
            f"-output {guest.disk1} "
            f"-input-charset utf-8 "
            f"-volid cidata "
            f"-rock "
            f"{userpath} {metapath}"
        )

    def create_from_image(self, guest):
        print("image")
        (name, size) = next(iter(guest.disks.items()))
        image = Image(guest, name, size)
        image.clone(self.config['path'])
        cdrom = Image(guest, "sr0")
        cdrom.cloud_init()
        self.instance['disk'] = [image.disk(), cdrom.disk()]
        print(f"disk: {image.path}")
            
    def create_from_boot(self, guest):
        print("boot")
        self.instance['location'] = self.config['location']
        self.instance['extra-args'] = guest.args
        for (name, size) in guest.disks.items():
            image = Image(guest, name, size)
            image.create()
            self.instance['disk'].append(image.disk())
            print(f"disk: {image.path}")
            
    def create(self, guest):
        print(f"create {guest.name}")
        self.create_instance(guest)
        if guest.image:
            self.create_from_image(guest)
        else:
            self.create_from_boot(guest)
        print(self.instance)
#        guest.instance = { 
#            'virt-type': 'kvm', 
#            'name':       guest.name,
#            'memory':     guest.memory,
#            'vcpus':      guest.cores, 
#            #'disk0':      guest.disk0 + ",device=disk",
#            #'disk1':      guest.disk1 + ",device=cdrom",
#            'os-type':    config['os-type'],
#            'os-variant': config['os-variant'],
#            #'network':    guest.network,
#            'graphics':   'none' 
#        }
#       self.create_cloud_init(guest)
#       image = self.clone_image(guest)
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
