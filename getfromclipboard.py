#!/usr/bin/env python3

import sys
import os
from subprocess import check_output

import get_platform

def _call_cmd(cmd):
    ret = ""
    try:
        ret = check_output(cmd)
    except OSError as oe:
        return False, None
    return True, ret

def _get_for_linux():
    r, c = _call_cmd(["xclip", "-sel", "clip", "-o"])
    if r:
        return c.decode("utf-8")
    else:
        print("Failed to call xclip. Make sure it is installed.")
        exit(1)

def _get_for_cygwin():
    r, c = _call_cmd(["cat", "/dev/clipboard"])
    if r:
        return c.decode("utf-8")
    else:
        print("Failed.")
        exit(1)

def getfromclipboard():

    contents = ""
    plat = get_platform.getplat()

    if plat == get_platform.PLAT_LINUX:
        contents = _get_for_linux()
    elif plat == get_platform.PLAT_CYGWIN:
        contents = _get_for_cygwin()
    else:
        print("Unsupported platform")
        return None

    return contents

if __name__ == "__main__":
    print(getfromclipboard())

