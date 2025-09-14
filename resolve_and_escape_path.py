#!/usr/bin/env python

import sys
import os

import path_utils

def puaq(selfhelp):
    print("Usage: %s /path/that has/spaces" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq(False)

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

