#!/usr/bin/env python

import sys
import os

import path_utils

def puaq():
    print("Usage: %s pid" % path_utils.basename_filtered(__file__))
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

    # another way to do it is os.system("echo \"call close(0)\" | gdb -p 3445")
    # because gdb will be reading from stdin
    os.system(cmd)

if __name__ == "__main__":

    # this script requires rootly powers

    if len(sys.argv) < 2:
        puaq()

    pid = sys.argv[1]
    close_all_fds(pid)

