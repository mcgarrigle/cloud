import os, re, yaml
import tempfile
import shutil
import subprocess
import secrets
import libvirt

class Process:

    # take lists of lists or tuples and return flattened list

    def flatten(self, a):
        return [y for x in a for y in x]

    def parameter(self, s):
        return f"--{s}"

    def expand(self, k, g):
        tuples = [(self.parameter(k), v) for v in g]
        return self.flatten(tuples)

    def scalar(self, v):
        return ((type(v) is str) or (type(v) is int))

    def argv(self, args):
        flags = [ self.parameter(k) for (k, v) in args.items() if v is None]
        singles = [ (self.parameter(k), str(v)) for (k, v) in args.items() if self.scalar(v)]
        groups = [ self.expand(k, v) for (k, v) in args.items() if type(v) is list]
        return flags + self.flatten(singles) + self.flatten(groups)

    def run(self, cmd, args):
        args = [cmd] + self.argv(args)
        print(' '.join(args))
        subprocess.call(args)
