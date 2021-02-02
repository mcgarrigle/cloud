import os
import tempfile
import yaml
import shutil
import subprocess
import secrets

from cloud import *

class Image:

    def __init__(self, guest, device, volume, size = 0):
        self.guest = guest
        self.device = device
        self.size = size
        if device == 'cdrom':
            extension = '.iso'
        else:
            extension = '.qcow2'
        self.path = os.path.join(IMAGE_ROOT, guest.name + '_' + volume + extension)

    def create(self):
        os.system(f"qemu-img create -f qcow2 {self.path} {self.size}")

    def clone(self, image):
        os.system(f"qemu-img create -f qcow2 -b {image} {self.path} {self.size}")

    def link(self, image):
        os.system(f"qemu-img create -f qcow2 -b {image} {self.path} {self.size}")

    def disk(self):
      return f"{self.path},device={self.device}"

    def user_data_path(self):
        local = os.path.join(os.environ['HOME'], ".cloud_config")
        if os.path.isfile(local):
            return local
        else:
            return os.path.join(ROOT, "metadata", "user-data")

    def cloud_init(self):
        print(self.path)
        root = tempfile.TemporaryDirectory()
        metapath = os.path.join(root.name, "meta-data")
        userpath = os.path.join(root.name, "user-data")
        metadata = {
            'instance-id': secrets.token_hex(15),
            'local-hostname': self.guest.hostname
        }
        self.write(metapath, metadata)
        shutil.copy(self.user_data_path(), userpath)
        os.system(f"genisoimage " 
            f"-joliet " 
            f"-output {self.path} "
            f"-input-charset utf-8 "
            f"-volid cidata "
            f"-rock "
            f"{userpath} {metapath}"
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
