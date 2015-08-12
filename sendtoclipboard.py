#!/usr/bin/env python

import sys
import os

def puaq():
    print("Usage: %s contents" % os.path.basename(__file__))
    sys.exit(1)

def sendtoclipboard(contents):
    os.system("inline_echo.py '%s' | xclip -sel clip" % contents)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    contents = ""
    for c in sys.argv[1:]:
        contents += c + " "
    contents = contents.strip()

    sendtoclipboard(contents)

