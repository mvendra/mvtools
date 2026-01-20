#!/usr/bin/env python

import sys
import os
import subprocess

import generic_run
import get_platform
import path_utils

def sendtoclipboard_linux(contents):
    if contents is None:
        return False, "Contents can't be None"
    v, r = generic_run.run_cmd_simple(["xsel", "--clipboard", "--input"], use_input=contents)
    if not v:
        return False, r
    return True, None

def sendtoclipboard_cygwin_or_msys_or_mingw(contents):
    if contents is None:
        return False, "Contents can't be None"
    try:
        with open("/dev/clipboard", "w") as f:
            f.write(contents)
    except:
        return False, "Unable to write to /dev/clipboard - exception raised"
    return True, None

def sendtoclipboard(contents):

    plat = get_platform.getplat()

    if plat == get_platform.PLAT_LINUX:
        return sendtoclipboard_linux(contents)
    if plat == get_platform.PLAT_CYGWIN or plat == get_platform.PLAT_MSYS or plat == get_platform.PLAT_MINGW:
        return sendtoclipboard_cygwin_or_msys_or_mingw(contents)

    clipboard_app = ""
    if plat == get_platform.PLAT_WINDOWS:
        clipboard_app = "clip"
    elif plat == get_platform.PLAT_MACOS:
        clipboard_app = "pbcopy"
    else:
        return False, "Unsupported platform"

    subprocess.call("inline_echo.py '%s' | %s" % (contents, clipboard_app), shell=True)
    return True, None

def puaq(selfhelp):
    print("Usage: %s contents" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq(False)

    v, r = sendtoclipboard(sys.argv[1])
    if not v:
        print(r)
        sys.exit(1)
