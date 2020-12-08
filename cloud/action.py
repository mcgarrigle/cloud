import os
import dns.resolver
from cloud.hypervisor import Hypervisor

class Action:

    def __init__(self):
        self.hypervisor = Hypervisor()

    def up(self, guest):
        print(f"up {guest.name}")
        if guest.state == 'undefined':
            self.hypervisor.create(guest)

    def down(self, guest):
        print(f"down {guest.name}")
        if guest.state != 'undefined':
            self.hypervisor.destroy(guest)

    def go(self, hostname):
        res = dns.resolver.Resolver()
        res.nameservers = ['192.168.122.1']
        answers = res.query(hostname + '.')
        ip = answers[0]
        os.system(f"ssh {ip}")
