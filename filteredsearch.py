#!/usr/bin/env python3

import os
import sys
import fsquery
from subprocess import check_output

import path_utils
import terminal_colors

def filteredsearch(path, search, extensions):

    ret = fsquery.makecontentlist(path, True, False, True, False, False, True, extensions)
    for r in ret:
        try:
            out = check_output(["ag", search, r])
            out = out.decode("ascii")
        except OSError as oe:
            print("Failed calling ag. Make sure silversearcher-ag is installed.")
            exit(1)
        if not len(out):
            continue
        print("%s%s" % (terminal_colors.TTY_BLUE, r))
        print("%s%s" % (terminal_colors.TTY_WHITE, out))

def puaq():
    print("Usage: %s path search extensions " % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 4:
        puaq()

    path = sys.argv[1]
    search = sys.argv[2]
    extensions = sys.argv[3:]

    filteredsearch(path, search, extensions)
