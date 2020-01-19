#!/usr/bin/env python3

# this is Filtered AG (silversearcher)

import os
import sys
import fsquery
from subprocess import check_output

def filteredag(path, search, extensions):

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
        print("\033[94m%s" % r)
        print("\033[0m%s" % out)

def puaq():
    print("Usage: %s path search extensions " % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 4:
        puaq()

    path = sys.argv[1]
    search = sys.argv[2]
    extensions = sys.argv[3:]

    filteredag(path, search, extensions)
