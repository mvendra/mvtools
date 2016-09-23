#!/usr/bin/env python

import sys
import os

from subprocess import call

import platform

def puaq():
    print("Usage: %s contents" % os.path.basename(__file__))
    sys.exit(1)

def sendtoclipboard(contents):
    clipboard_app = "xclip -sel clip" # for linux
    if platform.system() == "Darwin":
        clipboard_app = "pbcopy"
    call("inline_echo.py '%s' | %s" % (contents, clipboard_app), shell=True)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    contents = ""
    for c in sys.argv[1:]:
        contents += c + " "
    contents = contents.strip()

    sendtoclipboard(contents)

