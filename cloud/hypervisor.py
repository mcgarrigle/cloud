import os, re, yaml
import subprocess
import secrets
import libvirt
from cloud.domain import Domain

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
VIRT_ROOT = '/var/lib/libvirt/filesystems/'

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
        image = self.read(os.path.join(ROOT, "catalog", guest["image"] + ".yaml"))
        #guest = {**image, **guest}
        image.pop('name', None)  # key clash with guest
        guest.update(image)
        instance = os.path.join(VIRT_ROOT, guest['name'] + '.' + image['format'])
        guest['instance'] = instance
        os.system(f"qemu-img create -f qcow2 -b {image['path']} {instance} {guest['disk']}")

    def create_metadata(self, guest):
        metadata = os.path.join(ROOT, "metadata", "meta-data")
        userdata = os.path.join(ROOT, "metadata", "user-data")
        cloud_init = os.path.join(VIRT_ROOT, guest['name'] + '.iso')
        guest['cloud_init'] = cloud_init
        data = {
            'instance-id': secrets.token_hex(15),
            'local-hostname': guest.get('hostname', guest['name'])
        }
        self.write(metadata, data)
        os.system(f"genisoimage " 
            f"-joliet " 
            f"-input-charset utf-8 "
            f"-output {metadata} "
            f"-volid cidata "
            f"-rock {userdata} {metadata}"
        )

    def create(self, guest):
        print(f"create {guest}")
        self.create_instance(guest)
        self.create_metadata(guest)
        print(guest)
        args = { 
            'virt-type': 'kvm', 
            'name':       guest['name'],
            'memory':     guest.get('memory', '1024'),
            'vcpus':      guest.get('cores', '1'), 
            'disk0':      guest['instance'] + ",device=disk",
            'disk1':      guest['cloud_init'] + ",device=cdrom",
            'os-type':    guest['os-type'],
            'os-variant': guest['os-variant'],
            'network':    guest.get('network', 'default'),
            'graphics':   'none' 
        }
        args = ["virt-install", "--import", "--noautoconsole"] + self.argv(args)
        subprocess.call(args)

    def destroy(self, guest):
        domain = guest['name']
        os.system(f"virsh destroy --domain {domain}")
        os.system(f"virsh undefine --domain {domain}")
