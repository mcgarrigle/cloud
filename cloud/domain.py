import libvirt
import xml.etree.ElementTree as ET

class Domain:

    def __init__(self, domain):
        self.name  = domain.name()
        self.state = self._state(domain.state())
        if self.state == 'running':
            self.mac  = self._find_mac(domain)
            self.addr = self._find_address(domain)
        else:
            self.mac  = None
            self.addr = None

    def _find_mac(self, domain):
        tree = ET.fromstring(domain.XMLDesc(0))
        mac = tree.find("./devices/interface/mac")
        if mac is None:
            return None
        else:
            return mac.attrib['address']

    def _find_address(self, domain):
        addr = self._interfaceAddresses(domain, libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE)
        if addr: return addr
        addr = self._interfaceAddresses(domain, libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_ARP)
        if addr: return addr
        return self._interfaceAddresses(domain, libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT)

    def _interfaceAddresses(self, domain, source):
        nics = domain.interfaceAddresses(source)
        if nics:
            addrs = list(nics.values())[0]
            return self._addr(addrs['addrs'])
        else:
            return None

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
        if addrs: return addrs[0]['addr']
        return None
