
from ipaddress import *

class Interface:

    def __init__(self, name, defn):
        self.name = name
        self.connection = defn.get('connection', 'network=default')
        self.bootproto  = defn.get('bootproto', 'dhcp')
        if self.bootproto == 'static':
            self.addr    = IPv4Interface(defn['address'])
            self.netmask = self.addr.netmask
            self.gateway = IPv4Address(defn['gateway'])

    def to_virt_install(self):
        return self.connection

    def to_cloud_init_network_config(self):
        if self.bootproto == 'static':
            subnet = { 
                 'type': 'static',
                 'address': str(self.addr.ip),
                 'netmask': str(self.netmask),
                 'gateway': str(self.gateway)
               }
        else:
            subnet = { 'type': self.bootproto }

        blob = {
          'name':    self.name,
          'type':    'physical',
          'subnets': [ subnet ]
        }
        return blob

    def __repr__(self):
        return f"{self.name}: {self.addr}"
