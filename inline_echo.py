#!/usr/bin/env python3

import sys
import os

import path_utils

def inline_echo(msg):
    sys.stdout.write(msg)

def puaq(selfhelp): # Print Usage And Quit
    print("Usage: %s string_content" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        puaq(False)
    msg = sys.argv[1]
    inline_echo(msg)
