#!/usr/bin/env python

import sys
import os

def puaq():
    print("Usage: %s pid" % os.path.basename(__file__))
    sys.exit(1)

def list_fds(target):

    contents = os.listdir(target)
    ret = []
    for c in contents:
        if not os.path.isdir(c):
            ret.append(c)

    return ret

def close_all_fds(pid):

    fds = list_fds("/proc/%s/fd" % pid)
    cmd = "gdb -p %s " % pid
    for fd in fds:
        cmd += "-ex \"call close(%s)\" " % fd

    os.system(cmd)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    pid = sys.argv[1]
    close_all_fds(pid)

