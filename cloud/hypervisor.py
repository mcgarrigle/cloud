import os, re, yaml
import tempfile
import shutil
import subprocess
import secrets
import libvirt
from cloud.domain import Domain

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

class Hypervisor:

    def __init__(self):
        self.conn = libvirt.open()

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

    def parameter(self, s):
        return "--" + re.sub(r'\d$', '', s)

    def argv(self, args):
        params = [ (self.parameter(k), str(v)) for (k, v) in args.items() ]
        return [y for x in params for y in x]

    def create_instance(self, guest):
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

    def create(self, guest):
        print(f"create {guest.name}")
        self.create_cloud_init(guest)
        image = self.create_instance(guest)
        args = { 
            'virt-type': 'kvm', 
            'name':       guest.name,
            'memory':     guest.memory,
            'vcpus':      guest.cores, 
            'disk0':      guest.disk0 + ",device=disk",
            'disk1':      guest.disk1 + ",device=cdrom",
            'os-type':    image['os-type'],
            'os-variant': image['os-variant'],
            'network':    guest.network,
            'graphics':   'none' 
        }
        args = ["virt-install", "--import", "--noautoconsole"] + self.argv(args)
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
