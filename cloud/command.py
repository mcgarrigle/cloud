import re
import yaml
from cloud.guest import Guest
from cloud.action import Action
from cloud.hypervisor import Hypervisor

class Command:

    def __init__(self):
        self.domains = Hypervisor().domains()
        self.action  = Action()
        self.config  = self.load_config()
        self.project = self.config.get('project')
        self.guests  = [self.__new_guest(n,g) for n,g in self.config['guests'].items() ]

    def __new_guest(self, name, defn):
        if self.project:
            name = f"{self.project}-{name}"
        guest = Guest(name, defn)
        domain = self.domains.get(guest.name)
        if domain:
            guest.state = domain.state
            guest.addr  = domain.addr
        else:
            guest.state = 'undefined'
            guest.addr  = '-'
        return guest

    def commands(self):
        methods = list(dir(Command))
        return [f[5:] for f in methods if re.match(r'^_cmd_', f)]

    def load_config(self):
        try:
            with open('cloud.yaml') as f:
                return yaml.safe_load(f)
        except:
            print("cannot open cloud.yaml")
            exit(1)

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
        for guest in self.these(args):
            print(f"{guest.name: <15} {guest.state: <10} {guest.addr}")

    _cmd_ls = _cmd_list   # ls is synonym for list

    def _cmd_inventory(self, args):
        inv = {}
        for guest in self.guests:
            inv[guest.hostname] = { 'ansible_host': guest.addr }
        var = {}
        print(yaml.dump({ 'all': { 'hosts': inv, 'vars': var }}, default_flow_style=False))

    _cmd_inv = _cmd_inventory

    def _cmd_ssh_config(self, args):
        for guest in self.guests:
            print(f"Host {guest.hostname}")
            # print(f"  User cloud")
            print(f"  HostName {guest.addr}")

    def _cmd_up(self, args):
        for guest in self.these(args):
            self.action.up(guest)

    def _cmd_stop(self, args):
        for guest in self.these(args):
            self.action.stop(guest)

    def _cmd_down(self, args):
        for guest in self.these(args):
            self.action.down(guest)

    def _cmd_go(self, args):
        self.action.go(args[0])

    def run(self, cmd, args = []):
        method = f"self._cmd_{cmd}"
        fn = eval(method)
        fn(args)
