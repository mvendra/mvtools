#!/usr/bin/env python3

import sys
import os

from subprocess import call

import platform

def puaq():
    print("Usage: %s contents" % os.path.basename(__file__))
    sys.exit(1)

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

def sendtoclipboard(contents):

    clipboard_app = ""
    plat = getplat()

    if plat == "cygwin":
        call("inline_echo.py '%s' > /dev/clipboard" % (contents), shell=True)
        return

    if plat == "linux":
        clipboard_app = "xclip -sel clip" # for linux
    elif plat == "windows":
        clipboard_app = "clip"
    elif plat == "macosx":
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
