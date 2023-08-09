import os

class BlockDevice:

    def disk(self):
        return f"{self.path},device={self.driver}"

    def delete(self):
        print(f"deleting: {self.path}")
        if os.path.exists(self.path):
            os.remove(self.path)
        else:
            print("-- ERROR: the file does not exist")
