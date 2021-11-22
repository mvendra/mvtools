#!/usr/bin/env python3

import sys
import os
from subprocess import call

import get_platform
import path_utils

def sendtoclipboard(contents):

    plat = get_platform.getplat()

    if plat == get_platform.PLAT_CYGWIN:
        call("inline_echo.py '%s' > /dev/clipboard" % (contents), shell=True)
        return False

    clipboard_app = ""
    if plat == get_platform.PLAT_LINUX:
        clipboard_app = "xclip -sel clip" # for linux
    elif plat == get_platform.PLAT_WINDOWS:
        clipboard_app = "clip"
    elif plat == get_platform.PLAT_MACOSX:
        clipboard_app = "pbcopy"
    else:
        print("Unsupported platform")
        return False

    call("inline_echo.py '%s' | %s" % (contents, clipboard_app), shell=True)
    return True

def puaq():
    print("Usage: %s contents" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    if not sendtoclipboard(sys.argv[1]):
        sys.exit(1)
