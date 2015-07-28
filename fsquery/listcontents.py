#!/usr/bin/env python

import sys
import os

"""
        for f in filenames:
            for x in exts:
                if f.endswith(x): # mvtodo: and os.path.isfile() too !
                    ret_lists[x].append(os.path.join(os.path.abspath(dirpath), f))
"""

def makecontentlist(path, recursive, include_files, include_dirs, extensions):

    # mvtodo: update docstring
    """
    Makes a file list by walking the provided path
    path = a path string
    subs = a boolean, whether it should include subfolders (recursively)
    returns a dictionary with extensions as keys, and each dict entry is a list of filenames with full path
    """

    ret_list = []
    for dirpath, dirnames, filenames in os.walk(path):
        print("dirpath: %s" % dirpath)
        print("dirnames: %s" % dirnames)
        print("filenames: %s" % filenames)
    return ret_list

if __name__ == "__main__":
    
    if len(sys.argv) < 4:
        print("Usage: %s [-R] path include_files include_dirs extensions" % os.path.basename(__file__))
        exit(1)

    # declarations, defaults
    path = os.getcwd()
    rec = False
    inc_files = True
    inc_dirs = False
    exts = [] # empty means "any"

    # recursive - optional
    next_index = 1
    if '-R' in sys.argv or '-r' in sys.argv:
        rec = True
        next_index = 2

    # path - mandatory
    path = sys.argv[next_index]
    if not os.path.exists(path):
        print("%s does not exist." % path)
        sys.exit(1)
    next_index += 1

    # include files - mandatory
    if sys.argv[next_index] == "yes":
        inc_files = True
    elif sys.argv[next_index] == "no":
        inc_files = False
    next_index += 1

    # include dirs - mandatory
    if sys.argv[next_index] == "yes":
        inc_dirs = True
    elif sys.argv[next_index] == "no":
        inc_dirs = False
    next_index += 1

    # extensions - optional
    exts = sys.argv[next_index:]

    ret = makecontentlist(path, rec, inc_files, inc_dirs, exts)
    for r in ret:
        print(r)

