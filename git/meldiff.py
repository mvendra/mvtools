#!/usr/bin/python

import sys
import os

if __name__ == "__main__":
    if (len(sys.argv) < 8):
        print("This script is not intended for standalone use - integrate with meld instead.")
        sys.exit(1)
    os.system("meld %s %s" % (sys.argv[2], sys.argv[5]))

