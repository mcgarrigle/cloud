import os, re, yaml
import tempfile
import shutil
import subprocess
import secrets
import libvirt

class Process:

    def __init__(self, args):
        self.args = args

    # take lists of lists or tuples and return flattened list

    def flatten(self, a):
        return [y for x in a for y in x]

    def parameter(self, s):
        return f"--{s}"

    def expand(self, k, g):
        tuples = [(self.parameter(k), v) for v in g]
        return self.flatten(tuples)

    def args(self):
        singles = [ (self.parameter(k), str(v)) for (k, v) in args.items() if type(v) is str]
        groups = [ self.expand(k, v) for (k, v) in args.items() if type(v) is list]
        return self.flatten(singles) + self.flatten(groups)

    def run(self):
        args = ["virt-install", "--import", "--noautoconsole"] + self.argv(self.instance)
        print(' '.join(args))
        subprocess.call(args)
