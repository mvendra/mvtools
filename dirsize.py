#!/usr/bin/env python3

import sys
import os

from subprocess import run, PIPE

def get_dir_size(path, human):

    """ get_dir_size
    returns the disk usage size of a given path
    the 'human' parameter is a boolean flag.
    when true, it will return the size in
    human-readable form i.e. deriving the size unit (K, M, G, etc)
    when false, it will return the size in bytes.
    """

    #os.system("du -h %s | tail -n 1" % path)
    if human:
        cmd = ["du", "-h", path]
    else:
        cmd = ["du", "-b", path]

    p = run(cmd, stdout=PIPE, encoding="ascii")
    out = p.stdout

    # removes the last empty line
    nl = out.rfind("\n")
    if nl == -1:
        return None
    out = out[:nl]

    # removes the subdir detail list
    nl = out.rfind("\n")
    if nl != -1: #only if theres subfolders
        out = out[nl+1:]

    # removes the path
    esp = out.find("\t")
    if esp == -1:
        return None
    out = out[:esp]

    if human:
        return out
    else:
        return int(out)

def puaq():
    print("Usage: %s /path/to/folder" % os.path.basename(__file__))
    sys.exit(1)

def escape_spaces(thepath):
    theret = ""
    for i in thepath:
        if i == " ":
            theret += "\\"
        theret += i
    return theret

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    thepath = ""
    if len(sys.argv) > 2:
        for i in sys.argv[1:]:
            thepath += i + " "
        thepath = thepath[0:len(thepath)-1]
    else:
        thepath = sys.argv[1]

    thepath_escaped_abs = escape_spaces(os.path.abspath(thepath))
    thesize = get_dir_size(thepath, True)

    print("%s: %s" % (thepath_escaped_abs, thesize))

