#!/usr/bin/env python

import sys
import os

def puaq():
    print("Usage: %s contents" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    contents = ""
    for c in sys.argv[1:]:
        contents += c + " "
    contents = contents.strip()

    os.system("inline_echo.py '%s' | xclip -sel clip" % contents)

