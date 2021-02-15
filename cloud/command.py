import re
import sys
import yaml
import inspect
from cloud.guest import Guest
from cloud.action import Action
from cloud.hypervisor import Hypervisor

class Command:

    def __init__(self):
        domains = [ (d.name, d) for d in Hypervisor().domains() ]
        self.domains = dict(domains)
        self.action  = Action()

    def commands(self):
        functions = inspect.getmembers(Command, inspect.isfunction)
        methods = [ f for f in functions if re.match(r'^_cmd_', f[0]) ]
        mapping = [ (m[0][5:], inspect.getdoc(m[1])) for m in methods ]
        return mapping

    def __new_guest(self, name, defn):
        if self.project:
            name = f"{self.project}-{name}"
        guest = Guest(name, defn)
        domain = self.domains.get(guest.name)
        if domain:
            guest.state = domain.state
            guest.addr  = domain.addr
        return guest

    def load_config(self, path):
        try:
            with open(path) as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            sys.exit(f"cannot open {path}")
        self.version = self.config.get('version')
        if self.version == '2':
            pass
        else:
            sys.exit(f"version {self.version} not supported")
        self.project = self.config.get('project')
        self.guests  = [self.__new_guest(n,g) for n,g in self.config['guests'].items() ]

    def regex(self, glob):
        pattern = glob.replace('*', '.*')
        return re.compile(f"^{pattern}$")

    def these(self, args):
        if args:
            pattern = self.regex(args[0])
            return [ g for g in self.guests if pattern.match(g.name) ]
        else:
            return self.guests

    def _cmd_list(self, args):
        """ show status of all guests """
        for guest in self.these(args):
            print(f"{guest.name: <15} {guest.state: <10} {guest.addr}")

    _cmd_ls = _cmd_list   # ls is synonym for list

    def _cmd_inventory(self, args):
        """ create ansible inventory of all guests """
        inv = {}
        for guest in self.guests:
            inv[guest.hostname] = { 'ansible_host': guest.addr }
        var = {}
        print(yaml.dump({ 'all': { 'hosts': inv, 'vars': var }}, default_flow_style=False))

    _cmd_inv = _cmd_inventory

    def _cmd_ssh_config(self, args):
        """ create ssh_config file """
        for guest in self.guests:
            print(f"Host {guest.hostname}")
            print(f"  HostName {guest.addr}")

    def _cmd_up(self, args):
        """ create and start guests """
        for guest in self.these(args):
            self.action.up(guest)

    def _cmd_stop(self, args):
        """ halt all guests """
        for guest in self.these(args):
            self.action.stop(guest)

    def _cmd_down(self, args):
        """ destroy and undefine guests """
        for guest in self.these(args):
            self.action.down(guest)

    def _cmd_go(self, args):
        """ ssh to guest """
        self.action.go(args[0])

    def run(self, path, cmd, args = []):
        self.load_config(path)
        method = f"self._cmd_{cmd}"
        fn = eval(method)
        fn(args)
