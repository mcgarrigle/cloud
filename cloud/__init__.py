import os

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
CLOUD_IMAGES = os.environ.get('CLOUD_IMAGES') or '/var/lib/libvirt/images'
CLOUD_POOL = os.environ.get('CLOUD_POOL') or '/var/lib/libvirt/filesystems'
