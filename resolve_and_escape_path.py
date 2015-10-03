#!/usr/bin/env python

import sys
import os

def puaq():
    print("Usage: %s /path/that has/spaces" % os.path.basename(__file__))
    sys.exit(1)

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

    # do the escaping
    theres = ""
    for i in thepath:
        if i == " ":
            theres += "\\"
        theres += i

    print(theres)

