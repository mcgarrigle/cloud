import libvirt
import xml.etree.ElementTree as ET

class Domain:

    def __init__(self, domain):
        self.name   = domain.name()
        self.state  = self._state(domain.state())

        if self.state == 'running':
            tree = ET.fromstring(domain.XMLDesc(0))
            mac = tree.find("./devices/interface/mac")
            if mac is None:
                self.mac  = None
            else:
                self.mac = mac.attrib['address']

            nics = domain.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE)
            if len(nics) > 0:
              addrs = list(nics.values())[0]
              self.addr = self._addr(addrs['addrs'])
            else:
                self.addr = None
        else:
            self.mac  = None
            self.addr = None

    def _state(self, s):
        sw = {
            libvirt.VIR_DOMAIN_NOSTATE:     'none',
            libvirt.VIR_DOMAIN_RUNNING:     'running',
            libvirt.VIR_DOMAIN_BLOCKED:     'blocked',
            libvirt.VIR_DOMAIN_PAUSED:      'paused',
            libvirt.VIR_DOMAIN_SHUTDOWN:    'shutdown',
            libvirt.VIR_DOMAIN_SHUTOFF:     'shutoff',
            libvirt.VIR_DOMAIN_CRASHED:     'crashed',
            libvirt.VIR_DOMAIN_PMSUSPENDED: 'suspended',
        }
        return sw.get(s[0], "unknown")

    def _addr(self, addrs):
        if len(addrs) == 0:
            return None
        else:
            return addrs[0]['addr']
