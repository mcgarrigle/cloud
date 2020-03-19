import os
import yaml
import dns.resolver
from cloud.action import Action

class Command:

    def __init__(self):
        self.config = self.load_config()
        self.action = Action()
        self._ls = self._list   # ls is synonym for list
        guests = []
        for (k,v) in self.config['guests'].items():
            v['name'] = k
            guests.append(v)
        self.guests = guests

    def load_config(self):
        try:
            with open('cloud.yaml') as f:
                return yaml.safe_load(f)
        except:
            print("cannot open cloud.yaml")
            exit(1)

    def _help(self, args = []):
        print("help", args)

    def _list(self, args):
        for guest in self.guests:
            print(guest)

    def _up(self, args):
        for guest in self.guests:
            self.action.up(guest)

    def _down(self, args):
        for guest in self.guests:
            self.action.down(guest)

    def _go(self, args):
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
