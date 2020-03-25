#!/usr/bin/env python3

import sys
import os

from subprocess import call

if __name__ == "__main__":
    if (len(sys.argv) < 8):
        print("This script is not intended for standalone use - integrate with meld instead.")
        sys.exit(1)
    call("meld %s %s" % (sys.argv[2], sys.argv[5]), shell=True)

