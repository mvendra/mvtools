#!/usr/bin/env python

import sys
import os

import get_platform
import generic_run

def _get_for_linux():
    v, r = generic_run.run_cmd_simple(["xclip", "-sel", "clip", "-o"])
    if v:
        return r
    return None

def _get_for_cygwin_or_msys():
    contents = None
    try:
        with open("/dev/clipboard", "r") as f:
            contents = f.read()
    except:
        pass
    return contents

def getfromclipboard():

    contents = ""
    plat = get_platform.getplat()

    if plat == get_platform.PLAT_LINUX:

        contents = _get_for_linux()
        if contents is None:
            return False, "Failed getting clipboard. Make sure xclip is installed."

    elif plat == get_platform.PLAT_CYGWIN or plat == get_platform.PLAT_MSYS:

        contents = _get_for_cygwin_or_msys()
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
