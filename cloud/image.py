import os
import tempfile
import yaml
import shutil
import subprocess
import secrets

from cloud import *
from cloud.block_device import BlockDevice
from cloud.cache        import Cache

class Image(BlockDevice):

    def __init__(self, guest, device, size = 0):
        self.guest  = guest
        self.device = device
        self.size   = size
        self.driver = 'disk'
        self.path   = os.path.join(CLOUD_POOL, guest.name + '_' + device + '.qcow2')
        image = Cache().image("URL") 
        shutil.copyfile(image, self.path)
        os.system(f"qemu-img resize -q {self.path} {self.size}")
