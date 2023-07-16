import os

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
CLOUD_POOL = os.environ.get('CLOUD_POOL') or '/var/lib/libvirt/filesystems'
