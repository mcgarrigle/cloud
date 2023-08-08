import os
import tempfile
import yaml
import shutil
import subprocess
import secrets

from cloud import *

class Image:

    def __init__(self, guest, device, size = 0):
        self.guest = guest
        self.device = device
        self.size = size
        if device == 'sr0':
            self.driver = 'cdrom'
            extension = '.iso'
        else:
            self.driver = 'disk'
            extension = '.qcow2'
        self.path = os.path.join(CLOUD_POOL, guest.name + '_' + device + extension)

    def create(self):
        os.system(f"qemu-img create -q -f qcow2 {self.path} {self.size}")

    def clone(self, image):
        shutil.copyfile(image, self.path)
        os.system(f"qemu-img resize -q {self.path} {self.size}")

    def link(self, image):
        os.system(f"qemu-img create -q -f qcow2 -b {image} {self.path} {self.size}")

    def disk(self):
        return f"{self.path},device={self.driver}"
 
    def xdg_config_home(self):
        return os.environ['XDG_CONFIG_HOME'] or os.path.join(os.environ['HOME'], ".config")

    def user_data_path(self):
        path1 = os.path.join(self.xdg_config_home(), "cloud", "user-data")
        path2 = os.path.join(os.environ['HOME'], ".cloud_config")
        for path in [ path1, path2 ]:
          if os.path.isfile(path):
              return path
        return os.path.join(ROOT, "metadata", "user-data")

    def cloud_init_meta_data(self, path):
        metadata = {
            'instance-id': secrets.token_hex(15),
            'local-hostname': self.guest.hostname
        }
        self.write(path, metadata)

    def cloud_init_nameserver(self, config):
        config['type'] = 'nameserver'
        return config

    def cloud_init_network_config(self, path):
        blob = {
            'version': 1, 'config': [ i.to_cloud_init_network_config() for i in self.guest.interfaces ]
        }
        blob['config'].append(self.cloud_init_nameserver(self.guest.nameserver))
        self.write(path, blob)

    def cloud_init(self):
        root = tempfile.TemporaryDirectory()
        user_data_path      = self.user_data_path()
        meta_data_path      = os.path.join(root.name, "meta-data")
        network_config_path = os.path.join(root.name, "network-config")
        self.cloud_init_meta_data(meta_data_path)
        self.cloud_init_network_config(network_config_path)
        os.system(f"genisoimage " 
            f"-quiet " 
            f"-rock "
            f"-joliet " 
            f"-output {self.path} "
            f"-volid CIDATA "
            f"{user_data_path} {meta_data_path} {network_config_path}"
        )

    def write(self, path, data):
        with open(path, 'w') as f:
            f.write(yaml.dump(data))

    def delete(self):
        print(f"deleting: {self.path}")
        if os.path.exists(self.path):
            os.remove(self.path)
        else:
            print("-- ERROR: the file does not exist")
