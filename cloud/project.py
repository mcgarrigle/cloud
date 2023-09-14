import sys
import re

from cloud.guest import Guest

class Project:

    def guest_name(self, name):
        return '-'.join(filter(None,[self.name, name]))

    def __init__(self, config):
        self.version = config.get('version')
        if self.version == '3':
            pass
        else:
            sys.exit(f"version {self.version} not supported")
        self.name   = config.get('project')
        self.guests = [ Guest(self.guest_name(n), g) for n,g in config['guests'].items() ]

    def regex(self, glob):
        pattern = glob.replace('*', '.*')
        return re.compile(f"^{pattern}$")

    def these(self, args):
        if args:
            pattern = self.regex(args[0])
            return [ g for g in self.guests if pattern.match(g.name) ]
        else:
            return self.guests
