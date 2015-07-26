#!/usr/bin/env python

import sys
import os

def makefilelist(path, exts, subs):

    """
    Makes a file list by walking the provided path
    path = a path string
    exts = a list of extensions to consider, without the dot
    subs = a boolean, whether it should include subfolders (recursively)
    returns a dictionary with extensions as keys, and each dict entry is a list of filenames with full path
    """

    ret_lists = {}
    for x in exts:
        ret_lists[x] = []

    for dirpath, dirnames, filenames in os.walk(path):
        if not subs and dirpath != ".":
                break

        for f in filenames:
            for x in exts:
                if f.endswith(x):
                    ret_lists[x].append(os.path.join(os.path.abspath(dirpath), f))

    return ret_lists

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: %s [-R] path extensions" % os.path.basename(__file__))
        exit(1)

    inc_sub = False
    if '-R' in sys.argv or '-r' in sys.argv:
        inc_sub = True
        path = sys.argv[2]
        exts = sys.argv[3:]
    else:
        path = sys.argv[1]
        exts = sys.argv[2:]

    ret = makefilelist(path, exts, inc_sub)
    for k in ret:
        for r in ret[k]:
            print(r)

