import re
import inspect
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
        guest = Guest(f"{self.project}_{name}", defn)
        domain = self.domains.get(guest.name)
        if domain:
            guest.state = domain.state
            guest.addr  = domain.addr
        else:
            guest.state = 'undefined'
            guest.addr  = '-'
        return guest

    def load_config(self):
        try:
            with open('cloud.yaml') as f:
                return yaml.safe_load(f)
        except:
            print("cannot open cloud.yaml")
            exit(1)

    def _cmd_help(self, args = []):
        """ show help """
        print("cloud help")
        methods = sorted(list(dir(Command)))
        commands = [func for func in methods if re.match(r'^_cmd_[a-z]', func)]
        for command in commands:
            method = eval(f"self.{command}")
            print('*', command.lstrip('_cmd_'), '-', inspect.getdoc(method))

    def _cmd_list(self, args):
        """ show status of all guests """
        for guest in self.guests:
            print(f"{guest.name: <15} {guest.state: <10} {guest.addr}")

    _cmd_ls = _cmd_list   # ls is synonym for list

    def _cmd_inventory(self, args):
        """ create ansible inventory of all guests """
        inv = {}
        for guest in self.guests:
            inv[guest.name] = { 'ansible_host': guest.addr }
        var = { 'ansible_user': 'cloud' }
        print(yaml.dump({ 'all': { 'hosts': inv, 'vars': var }}, default_flow_style=False))

    _cmd_inv = _cmd_inventory

    def _cmd_ssh_config(self, args):
        """ create ssh_config file """
        for guest in self.guests:
            print(f"Host {guest.name}")
            print(f"  User cloud")
            print(f"  HostName {guest.addr}")

    def _cmd_up(self, args):
        """ create and start guests """
        for guest in self.guests:
            self.action.up(guest)

    def _cmd_down(self, args):
        """ destroy and undefine guests """
        for guest in self.guests:
            self.action.down(guest)

    def _cmd_go(self, args):
        """ ssh to guest """
        self.action.go(args[0])

    def run(self, cmd, args = []):
        try:
            method = f"self._cmd_{cmd}"
            fn = eval(method)
        except:
            print(f"no such command '{cmd}'")
            exit(1)
        fn(args)
