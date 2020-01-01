#!/usr/bin/env python3

import sys
import os

def inline_echo(msg):
    sys.stdout.write(msg)

def puaq(): # Print Usage And Quit
    print("Usage: %s string_content" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        puaq()
    msg = sys.argv[1]
    inline_echo(msg)
