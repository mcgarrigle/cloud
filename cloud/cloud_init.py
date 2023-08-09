import os
import tempfile
import yaml
import shutil
import subprocess
import secrets

from cloud import *
from cloud.config       import Config
from cloud.block_device import BlockDevice

class CloudInit(BlockDevice):

    def __init__(self, guest):
        self.guest  = guest
        self.driver = 'cdrom'
        self.path = os.path.join(CLOUD_POOL, guest.name + '_sr0.iso')
        temp = tempfile.TemporaryDirectory()
        user_data_path      = Config.cloud_config_path()
        meta_data_path      = os.path.join(temp.name, "meta-data")
        network_config_path = os.path.join(temp.name, "network-config")
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

    def cloud_init_meta_data(self, path):
        metadata = {
            'instance-id': secrets.token_hex(15),
            'local-hostname': self.guest.hostname
        }
        self.write(path, metadata)

    def nameserver(self, config):
        config['type'] = 'nameserver'
        return config

    def cloud_init_network_config(self, path):
        blob = {
            'version': 1, 'config': [ i.to_cloud_init_network_config() for i in self.guest.interfaces ]
        }
        blob['config'].append(self.nameserver(self.guest.nameserver))
        self.write(path, blob)

    def write(self, path, data):
        with open(path, 'w') as f:
            f.write(yaml.dump(data))
