import subprocess

# take lists of lists or tuples and return flattened list

def flatten(a):
    return [y for x in a for y in x]

def parameter(s):
    return f"--{s}"

def expand(k, g):
    tuples = [ (parameter(k), v) for v in g ]
    return flatten(tuples)

def scalar(v):
    return isinstance(v, (str, int, float))

def argv(args):
    flags   = [ parameter(k) for (k, v) in args.items() if v is None ]
    singles = [ (parameter(k), str(v)) for (k, v) in args.items() if scalar(v) ]
    groups  = [ expand(k, v) for (k, v) in args.items() if type(v) is list ]
    return flags + flatten(singles) + flatten(groups)

def run(cmd, args):
    args = [cmd] + argv(args)
    subprocess.call(args)
