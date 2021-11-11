#!/usr/bin/env python3

import sys
import os

import path_utils
import get_platform
import generic_run
import mvtools_exception

def checkmounted_linux(path):

    v, r = generic_run.run_cmd_simple(["mount"])
    if not v:
        raise mvtools_exception.mvtools_exception("Unable to launch mount's subprocess")
    mount_output = r.strip()

    path = " " + path + " " # disallows partial matches
    if mount_output.find(path) > 0:
        return True
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
    path_to_find = path_utils.filter_remove_trailing_sep(path_to_find, "no")
    path_to_find = os.path.abspath(path_to_find)

    if checkmounted(path_to_find):
        print("[%s] is mounted." % path_to_find)
        sys.exit(0)
    else:
        print("[%s] is not mounted." % path_to_find)
        sys.exit(1)
