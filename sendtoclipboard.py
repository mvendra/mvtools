#!/usr/bin/env python

import sys
import os

from subprocess import call

def puaq():
    print("Usage: %s contents" % os.path.basename(__file__))
    sys.exit(1)

def sendtoclipboard(contents):
    call("inline_echo.py '%s' | xclip -sel clip" % contents, shell=True)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    contents = ""
    for c in sys.argv[1:]:
        contents += c + " "
    contents = contents.strip()

    sendtoclipboard(contents)

