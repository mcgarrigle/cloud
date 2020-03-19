#!/usr/bin/python3

import dns.resolver

my_resolver = dns.resolver.Resolver()

# 8.8.8.8 is Google's public DNS server
my_resolver.nameservers = ['192.168.122.1']

answers = my_resolver.query('puppet.')
for answer in answers:
    print(answer)
