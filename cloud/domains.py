import libvirt
from cloud.domain import Domain

class Domains:

    def __init__(self):
        self.conn = libvirt.open()

    def list(self):
        domains = {}
        for d in self.conn.listAllDomains():
            domain = Domain(d)
            domains[domain.name] = domain
        return domains
