import libvirt
import xml.etree.ElementTree as ET

class Domain:

    def __init__(self, domain):
        self.name   = domain.name()
        self.state  = self._state(domain.state())
        #em = root.findall("./devices/interface[@type='bridge']/mac")
        #print(em[0].attrib['address'])

        if self.state == 'running':
            self.addr = self._addr(domain.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE))
            tree = ET.fromstring(domain.XMLDesc(0))
            mac = tree.findall("./devices/interface/mac")
            if len(mac) > 0:
                self.mac = mac[0].attrib['address']
            else:
                self.mac = '-'
        else:
            self.mac  = '-'
            self.addr = '-'

    def _state(self, s):
        sw = {
            libvirt.VIR_DOMAIN_NOSTATE: 'none',
            libvirt.VIR_DOMAIN_RUNNING: 'running',
            libvirt.VIR_DOMAIN_BLOCKED: 'blocked',
            libvirt.VIR_DOMAIN_PAUSED: 'paused',
            libvirt.VIR_DOMAIN_SHUTDOWN: 'shutdown',
            libvirt.VIR_DOMAIN_SHUTOFF: 'shutoff',
            libvirt.VIR_DOMAIN_CRASHED: 'crashed',
            libvirt.VIR_DOMAIN_PMSUSPENDED: 'suspended',
        }
        return sw.get(s[0], "unknown")

    def _addr(self, nics):
        if len(nics) == 0:
            return '-'
        else:
            nic = list(nics.values())[0]
            return  nic['addrs'][0]['addr']
