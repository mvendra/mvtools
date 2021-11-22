#!/usr/bin/env python3

import os
import sys
from subprocess import check_output
from subprocess import CalledProcessError

import path_utils
import fsquery
import mvtools_exception
import terminal_colors

def filteredsearch(path, search, extensions):

    v, r = fsquery.makecontentlist(path, True, False, True, False, False, False, True, extensions)
    if not v:
        raise mvtools_exception.mvtools_exception(r)
    ret = r
    for r in ret:
        out = ""
        try:
            out = check_output(["ag", search, r])
            out = out.decode("utf8")
        except OSError as oe:
            print("Failed calling ag. Make sure silversearcher-ag is installed.")
            exit(1)
        except CalledProcessError:
            pass # no match, most likely
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
