
from cloud.hypervisor import Hypervisor

class Action:

    def __init__(self):
        self.hypervisor = Hypervisor()

    def up(self, guest):
        print("up", guest)
        self.hypervisor.create(guest)

    def down(self, guest):
        print("up", guest)
        self.hypervisor.destroy(guest)

