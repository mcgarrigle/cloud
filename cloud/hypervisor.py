
import os
import re
import yaml

class Hypervisor:

    def __init__(self):
        pass

    def parameter(self, s):
        return "--" + re.sub(r'\d$', '', s)

    def argv(self, args):
        params = [ (self.parameter(k), str(v)) for (k, v) in args.items() ]
        return [y for x in params for y in x]

    def create_instance(self, image, instance):
        path = os.path.join("index", image)
        os.system(f"cp {path} {instance}")

    def create_metadata(self, metadata, guest):
        os.system(f"genisoimage -output {metadata} -volid cidata -joliet -rock metadata/user-data metadata/meta-data")

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
            'os-type': 'Linux', 
            'os-variant': 'centos7.0', 
            'virt-type': 'kvm', 
            'network': 'default', 
            'graphics': 'none' 
        }
        print(self.argv(args))
        command = ["virt-install", "--import", "--noautoconsole"] + self.argv(args)
        print(command)
        os.system(' '.join(command))
