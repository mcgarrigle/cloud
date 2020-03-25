import os
import re
import inspect
import yaml
import dns.resolver
from cloud.action  import Action
from cloud.domains import Domains
from cloud.domain  import Domain

class Command:

    def __init__(self):
        self._ls = self._list   # ls is synonym for list
        self.domains = Domains().list()
        self.config  = self.load_config()
        self.action  = Action()
        guests = []
        for (name, guest) in self.config['guests'].items():
            self.guest_state(name, guest)
            guests.append(guest)
        self.guests = guests

    def guest_state(self, name,  guest):
        guest['name'] = name
        domain = self.domains.get(name)
        if domain:
            guest['state'] = domain.state
            guest['addr']  = domain.addr
        else:
            guest['state'] = 'undefined'
            guest['addr']  = '-'

    def load_config(self):
        try:
            with open('cloud.yaml') as f:
                return yaml.safe_load(f)
        except:
            print("cannot open cloud.yaml")
            exit(1)

    def _help(self, args = []):
        """ show help """
        print("cloud help")
        methods = [func for func in dir(Command) if re.match(r'^_[a-z]', func)]
        for method in sorted(list(methods)):
            print('*', method.lstrip('_'), '-', inspect.getdoc(eval(f"self.{method}")))

    def _list(self, args):
        """ show status of all guests """
        domains = Domains().list()
        for guest in self.guests:
            print(f"{guest['name']: <15} {guest['state']: <10} {guest['addr']}")

    def _up(self, args):
        """ create and start guests """
        for guest in self.guests:
            self.action.up(guest)

    def _down(self, args):
        """ destroy and undefine guests """
        for guest in self.guests:
            self.action.down(guest)

    def _go(self, args):
        """ ssh to guest """
        res = dns.resolver.Resolver()
        res.nameservers = ['192.168.122.1']
        answers = res.query(args[0] + '.')
        ip = answers[0]
        print(f"ssh cloud@{ip}")
        os.system(f"ssh cloud@{ip}")

    def run(self, cmd, args):
        try:
            method = f"self._{cmd}"
            fn = eval(method)
        except:
            print(f"no such command '{cmd}'")
            exit(1)
        fn(args)
