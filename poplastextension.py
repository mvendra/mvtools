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
    print(filename[:filename.rfind(".")])

