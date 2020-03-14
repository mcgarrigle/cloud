
from cloud.action import Action

class Command:

    def __init__(self):
        self.action = Action()

    def help(self, args = []):
        print("help", args)

    def _list(self, args):
        print("list", args)
        self.action.list()

    def _up(self, args):
        print("up", args)

    def run(self, cmd, args):
        try:
            method = f"self._{cmd}"
            fn = eval(method)
        except:
            print(f"no such command '{cmd}'")
            exit(1)
        fn(args)
