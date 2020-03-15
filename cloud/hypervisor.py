
import os, re, yaml
import secrets

class Hypervisor:

    def __init__(self):
        pass

    def write(self, path, data):
        with open(path, 'w') as f:
            f.write(yaml.dump(data))

    def parameter(self, s):
        return "--" + re.sub(r'\d$', '', s)

    def argv(self, args):
        params = [ (self.parameter(k), str(v)) for (k, v) in args.items() ]
        return [y for x in params for y in x]

    def create_instance(self, image, instance):
        path = os.path.join("index", image)
        os.system(f"cp {path} {instance}")

    def create_metadata(self, metadata, guest):
        data = {
            'instance-id': secrets.token_hex(15),
            'local-hostname': guest['name']
        }
        self.write("metadata/meta-data", data)
        os.system(f"genisoimage -input-charset utf-8 -output {metadata} -volid cidata -joliet -rock metadata/user-data metadata/meta-data")

    def create(self, guest):
        name = guest['name']
        print(f"create {name} {guest}")
        machine  = f"machines/{name}.qcow2c"
        metadata = f"machines/{name}.iso"
        self.create_instance("centos7", machine)
        self.create_metadata(metadata, guest)
        args = { 
            'name': name,
            'memory': '1024', 
            'vcpus': '1', 
            'disk0': f"{machine},device=disk",
            'disk1': f"{metadata},device=cdrom",
            'virt-type': 'kvm', 
            'os-type': 'Linux', 
            'os-variant': 'centos7.0', 
            'network': 'default', 
            'graphics': 'none' 
        }
        args = ["virt-install", "--import", "--noautoconsole"] + self.argv(args)
        command = ' '.join(args) 
        os.system(command)

    def destroy(self, guest):
        domain = guest['name']
        os.system(f"virsh destroy --domain {domain}")
        os.system(f"virsh undefine --domain {domain}")
