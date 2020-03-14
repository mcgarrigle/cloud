
import yaml

class Action:

    def __init__(self):
        self.config = self.load_config()

    def load_config(self):
        try:
            with open('cloud.yaml') as f:
                return yaml.safe_load(f)
        except:
            print("cannot open cloud.yaml")
            exit(1)

    def guests(self):
      return self.config['guests'].items()

    def list(self):
        for (name, guest) in self.guests():
            print(name, guest) 
