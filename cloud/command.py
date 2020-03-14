
import yaml
from cloud.action import Action

class Command:

    def __init__(self):
        self.config = self.load_config()
        self.action = Action()
        self._ls = self._list

    def load_config(self):
        try:
            with open('cloud.yaml') as f:
                return yaml.safe_load(f)
        except:
            print("cannot open cloud.yaml")
            exit(1)

    def guests(self):
      return self.config['guests'].items()

    def help(self, args = []):
        print("help", args)

    def _list(self, args):
        print("list", args)
        for (name, guest) in self.guests():
            print(name, guest)

    def _up(self, args):
        print("up", args)
        for (name, guest) in self.guests():
            self.action.up(name, guest)

    def run(self, cmd, args):
        try:
            method = f"self._{cmd}"
            fn = eval(method)
        except:
            print(f"no such command '{cmd}'")
            exit(1)
        fn(args)
