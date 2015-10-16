#!/usr/bin/env python

import sys
import os

def puaq():
    print("Usage: %s thefile.with.several.extensions" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    filename = sys.argv[1]
    result = "you_found_a_bug"
    idx = filename.rfind(".")

    if idx == -1:
        # no extensions found at all.
        result = filename + "_sub"
    else:
        result = filename[:idx]

    print(result)

