#!/usr/bin/env python3

import sys
import os
from subprocess import call

import get_platform
import mvtools_exception
import path_utils

def checkmounted_linux(path):

    # disallows partial matches
    path = " " + path + " "

    ret = os.popen("mount").read().strip()
    if ret.find(path) > 0:
        return True
    else:
        return False

def checkmounted_cygwin(path):
    return os.path.ismount(path)

def checkmounted(path):

    """
    checkmounted
    checks if path is mounted
    returns True if it is, False if it is not
    """

    if get_platform.getplat() == get_platform.PLAT_LINUX:
        return checkmounted_linux(path)
    if get_platform.getplat() == get_platform.PLAT_CYGWIN:
        return checkmounted_cygwin(path)
    raise mvtools_exception.mvtools_exception("Unsupported platform")

def puaq():
    print("Usage: %s /mnt/path" % path_utils.basename_filtered(__file__))
    sys.exit(1)

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
        print("[%s] is mounted." % path_to_find)
        sys.exit(0)
    else:
        print("[%s] is not mounted." % path_to_find)
        sys.exit(1)
