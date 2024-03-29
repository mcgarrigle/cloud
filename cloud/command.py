import re
import sys
import yaml
import inspect

from cloud.project import Project
from cloud.guest import Guest
from cloud.action import Action
from cloud.hypervisor import Hypervisor

class Command:

    def __init__(self):
        self.hypervisor = Hypervisor()
        self.action     = Action()

    def commands(self):
        functions = inspect.getmembers(Command, inspect.isfunction)
        methods = [ f for f in functions if re.match(r'^_cmd_', f[0]) ]
        mapping = [ (m[0][5:], inspect.getdoc(m[1])) for m in methods ]
        return mapping

    def load_cloud_yaml(self, path):
        try:
            with open(path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            sys.exit(f"cannot open {path}\n{str(e)}")

    def empty(self, p):
        if p is None:
            return('-')
        else:
            return str(p)

    # add domain status to a guest

    def status(self, guest):
        domain = self.hypervisor.domain(guest.name)
        if domain:
            guest.state = domain.state
            guest.mac   = domain.mac
            guest.addr  = guest.addr or domain.addr
        return guest

    def _cmd_list(self, args):
        """ show status of all guests """
        up = 1
        for guest in self.project.these(args):
            guest = self.status(guest)
            print(f"{guest.name: <15} {guest.state: <10} {self.empty(guest.mac): <18} {self.empty(guest.addr)}")
            if guest.addr == '-':
                up = 0
        exit(up)

    _cmd_ls = _cmd_list   # ls is synonym for list

    def _cmd_wait(self, args):
        """ wait for all guests to boot """
        while True:
           booting = any([ a.addr == '-' for a in self.project.these(args) ])
           print(booting)
           if not booting: break

    def _cmd_inventory(self, args):
        """ create ansible inventory of all guests """
        inv = {}
        for guest in self.project.guests:
            guest = self.status(guest)
            inv[guest.hostname] = { 'ansible_host': guest.addr }
        var = {}
        print(yaml.dump({ 'all': { 'hosts': inv, 'vars': var }}, default_flow_style=False))

    _cmd_inv = _cmd_inventory

    def _cmd_ssh_config(self, args):
        """ create ssh_config file """
        for guest in self.project.guests:
            print(f"Host {guest.hostname}")
            print(f"  HostName {self.empty(guest.addr)}")

    def _cmd_up(self, args):
        """ create and start guests """
        for guest in self.project.these(args):
            self.action.up(self.status(guest))

    def _cmd_stop(self, args):
        """ halt all guests """
        for guest in self.project.these(args):
            self.action.stop(self.status(guest))

    def _cmd_down(self, args):
        """ destroy and undefine guests """
        for guest in self.project.these(args):
            self.action.down(self.status(guest))

    def _cmd_go(self, args):
        """ ssh to guest """
        self.action.go(args[0])

    def run(self, path, cmd, args = []):
        config = self.load_cloud_yaml(path)
        self.project = Project(config)
        method = f"self._cmd_{cmd}"
        fn = eval(method)
        fn(args)
