#!/usr/bin/env python3

import sys
import os

from subprocess import call

def puaq():
    print("Usage: %s /mnt/path" % os.path.basename(__file__))
    sys.exit(1)

def checkmounted(path):

    """
    checkmounted
    checks if path is mounted
    returns True if it is, False if it is not
    """

    # disallows partial matches
    path = " " + path + " "

    ret = os.popen("mount").read().strip()
    if ret.find(path) > 0:
        return True
    else:
        return False

if __name__ == "__main__":

    """
    check_mounted.py
    Checks if the given path is mounted
    returns 0 if the provided path is mounted
    return 1 if the provided path is NOT mounted
    """

    if len(sys.argv) < 2:
        puaq()

    path_to_find = sys.argv[1]
    if path_to_find[len(path_to_find)-1] == os.sep: # allows the input path to come with a trailing separator
        path_to_find = path_to_find[:len(path_to_find)-1]

    if checkmounted(path_to_find):
        exit(0)
    else:
        exit(1)

