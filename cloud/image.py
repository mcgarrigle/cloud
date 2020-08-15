import os
import tempfile
import shutil
import subprocess
import secrets

from cloud import IMAGE_ROOT

class Image:

    def __init__(self, guest_name, volume, size):
        self.path = os.path.join(IMAGE_ROOT, guest_name + '_' + volume)
        self.size = size

    def create(self):
        self.device = 'disk'
        self.path = self.path + '.qcow2'
        os.system(f"qemu-img create -f qcow2 {self.path} {self.size}")

    def clone(self, image):
        self.device = 'disk'
        self.path = self.path + '.qcow2'
        os.system(f"qemu-img create -f qcow2 -b {image} {self.path} {self.size}")

    def disk(self):
      return f"{self.path},device={self.device}"

    def user_data_path(self):
        local = os.path.join(os.environ['HOME'], ".cloud_config")
        if os.path.isfile(local):
            return local
        else:
            return os.path.join(ROOT, "metadata", "user-data")

    def cloud_init(self, guest):
        self.device = 'cdrom'
        self.path = self.path + '.iso'
        root = tempfile.TemporaryDirectory()
        metapath = os.path.join(root.name, "meta-data")
        userpath = os.path.join(root.name, "user-data")
        metadata = {
            'instance-id': secrets.token_hex(15),
            'local-hostname': guest.hostname
        }
        self.write(metapath, metadata)
        shutil.copy(user_data_path(), userpath)
        print(path)
        os.system(f"genisoimage " 
            f"-joliet " 
            f"-output {self.path} "
            f"-input-charset utf-8 "
            f"-volid cidata "
            f"-rock "
            f"{userpath} {metapath}"
        )

    def delete(self):
        if os.path.exists(self.path):
            os.remove(self.path)
        else:
            print("The file does not exist")
