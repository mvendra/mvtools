#!/usr/bin/env python3

import sys
import os
from subprocess import call

import get_platform

def puaq():
    print("Usage: %s contents" % os.path.basename(__file__))
    sys.exit(1)

def sendtoclipboard(contents):

    clipboard_app = ""
    plat = get_platform.getplat()

    if plat == get_platform.PLAT_CYGWIN:
        call("inline_echo.py '%s' > /dev/clipboard" % (contents), shell=True)
        return

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

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    contents = ""
    for c in sys.argv[1:]:
        contents += c + " "
    contents = contents.strip()

    sendtoclipboard(contents)
