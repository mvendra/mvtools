#!/usr/bin/env python3

import sys
import os
import subprocess

import generic_run
import get_platform
import path_utils

def sendtoclipboard_linux(contents):
    v, r = generic_run.run_cmd_simple(["xsel", "--clipboard", "--input"], use_input=contents)
    if not v:
        return False, r
    return True, None

def sendtoclipboard_cygwin(contents):
    subprocess.call("inline_echo.py '%s' > /dev/clipboard" % (contents), shell=True)
    return True, None

def sendtoclipboard(contents):

    plat = get_platform.getplat()

    if plat == get_platform.PLAT_LINUX:
        return sendtoclipboard_linux(contents)
    if plat == get_platform.PLAT_CYGWIN:
        return sendtoclipboard_cygwin(contents)

    clipboard_app = ""
    if plat == get_platform.PLAT_WINDOWS:
        clipboard_app = "clip"
    elif plat == get_platform.PLAT_MACOSX:
        clipboard_app = "pbcopy"
    else:
        return False, "Unsupported platform"

    subprocess.call("inline_echo.py '%s' | %s" % (contents, clipboard_app), shell=True)
    return True, None

def puaq():
    print("Usage: %s contents" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    v, r = sendtoclipboard(sys.argv[1])
    if not v:
        print(r)
        sys.exit(1)
