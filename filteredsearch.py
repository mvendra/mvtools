#!/usr/bin/env python3

import os
import sys

import mvtools_exception
import path_utils
import fsquery
import generic_run
import terminal_colors

def filteredsearch(path, search, extensions):

    v, r = fsquery.makecontentlist(path, True, False, True, False, False, False, True, extensions)
    if not v:
        raise mvtools_exception.mvtools_exception(r)
    targets = r

    for tg in targets:

        v, r = generic_run.run_cmd_simple(["ag", search, tg])
        if v:
            print("%s%s" % (terminal_colors.TTY_BLUE, tg))
            print("%s%s" % (terminal_colors.TTY_WHITE, r))

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
