#!/usr/bin/env python3

import sys
import os
import platform
from subprocess import check_output

def getplat():
    ps = platform.system().lower()
    if ps == "linux":
        return "linux"
    elif ps == "windows":
        return "windows"
    elif "cygwin_nt-10" in ps:
        return "cygwin"
    elif ps == "darwin":
        return "macosx"
    return ""

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
        return c.decode("ascii")
    else:
        print("Failed to call xclip. Make sure it is installed.")
        exit(1)

def _get_for_cygwin():
    r, c = _call_cmd(["cat", "/dev/clipboard"])
    if r:
        return c.decode("ascii")
    else:
        print("Failed.")
        exit(1)

def getfromclipboard():

    contents = ""
    plat = getplat()

    if plat == "linux":
        contents = _get_for_linux()
    elif plat == "cygwin":
        contents = _get_for_cygwin()
    else:
        print("Unsupported platform")
        return None

    return contents

if __name__ == "__main__":
    print(getfromclipboard())

