
import os, re, yaml
import secrets

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

class Hypervisor:

    def __init__(self):
        pass

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
        image.pop('name', None)  # key clash with guest
        guest.update(image)
        instance = os.path.join(ROOT, 'machines', guest['name'] + '.' + image['format'])
        guest['instance'] = instance
        os.system(f"qemu-img create -f qcow2 -b {image['path']} {instance} 10G")

    def create_metadata(self, guest):
        metadata = os.path.join(ROOT, 'machines', guest['name'] + '.iso')
        guest['metadata'] = metadata
        data = {
            'instance-id': secrets.token_hex(15),
            'local-hostname': guest['name']
        }
        self.write("metadata/meta-data", data)
        os.system(f"genisoimage -input-charset utf-8 -output {metadata} -volid cidata -joliet -rock metadata/user-data metadata/meta-data")

    def create(self, guest):
        print(f"create {guest}")
        self.create_instance(guest)
        self.create_metadata(guest)
        print(guest)
        args = { 
            'name': guest['name'],
            'memory': '1024', 
            'vcpus': '1', 
            'disk0': f"{guest['instance']},device=disk",
            'disk1': f"{guest['metadata']},device=cdrom",
            'virt-type': 'kvm', 
            'os-type': 'Linux', 
            'os-variant': 'centos7.0', 
            'network': 'default', 
            'graphics': 'none' 
        }
        args = ["virt-install", "--import", "--noautoconsole"] + self.argv(args)
        os.system(' '.join(args))

    def destroy(self, guest):
        domain = guest['name']
        os.system(f"virsh destroy --domain {domain}")
        os.system(f"virsh undefine --domain {domain}")
