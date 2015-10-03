#!/usr/bin/env python

import sys
import os

def puaq():
    print("Usage: %s \"/path/path has/spaces\"" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()
    thepath = sys.argv[1]
    theres = ""
    for i in thepath:
        if i == " ":
            theres += "\\"
        theres += i
    print(theres)

