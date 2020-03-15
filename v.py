import libvirt
conn = libvirt.open()

for domain in conn.listAllDomains():
    print(domain)
    #metadata = domain.metadata(libvirt.VIR_DOMAIN_METADATA_ELEMENT, "http://spinup.io/instance")
    print(domain.name())
    nif = domain.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE)
    print(nif)
