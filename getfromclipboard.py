#!/usr/bin/env python3

import sys
import os
import subprocess

import get_platform

def _call_cmd(cmd):
    ret = ""
    try:
        ret = subprocess.check_output(cmd)
    except OSError as oe:
        return False, None
    return True, ret

def _get_for_linux():
    v, r = _call_cmd(["xclip", "-sel", "clip", "-o"])
    if v:
        return r.decode("utf-8")
    return None

def _get_for_cygwin():
    v, r = _call_cmd(["cat", "/dev/clipboard"])
    if v:
        return r.decode("utf-8")
    return None

def getfromclipboard():

    contents = ""
    plat = get_platform.getplat()

    if plat == get_platform.PLAT_LINUX:

        contents = _get_for_linux()
        if contents is None:
            return False, "Failed getting clipboard. Make sure xclip is installed."

    elif plat == get_platform.PLAT_CYGWIN:

        contents = _get_for_cygwin()
        if contents is None:
            return False, "Failed getting clipboard."

    else:
        return False, "Unsupported platform"

    return True, contents

if __name__ == "__main__":

    v, r = getfromclipboard()
    print(r)
    if not v:
        sys.exit(1)
