import os

from cloud import *
from cloud.block_device import BlockDevice

class Disk(BlockDevice):

    def __init__(self,guest, device, size = 0):
        self.device = device
        self.size   = size
        self.driver = 'disk'
        self.path = os.path.join(CLOUD_POOL, guest.name + '_' + device + '.qcow2')
        os.system(f"qemu-img create -q -f qcow2 {self.path} {self.size}")
