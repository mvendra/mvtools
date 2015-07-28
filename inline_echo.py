#!/usr/bin/env python

import sys
import os

def puaq(): # Print Usage And Quit
    print("Usage: %s string_content" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        puaq()
    sys.stdout.write(sys.argv[1])

