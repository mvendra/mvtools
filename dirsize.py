#!/usr/bin/env python

import sys
import os

def puaq():
    print("Usage: %s /path/to/folder" % os.path.basename(__file__))
    sys.exit(1)

def escape_spaces(thepath):
    theret = ""
    for i in thepath:
        if i == " ":
            theret += "\\"
        theret += i
    return theret

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    thepath = ""
    if len(sys.argv) > 2:
        for i in sys.argv[1:]:
            thepath += i + " "
        thepath = thepath[0:len(thepath)-1]
    else:
        thepath = sys.argv[1]

    thepath_escaped_abs = escape_spaces(os.path.abspath(thepath))
    os.system("du -h %s | tail -n 1" % thepath_escaped_abs)

