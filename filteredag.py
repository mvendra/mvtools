#!/usr/bin/env python

# this is Filtered AG (silversearcher)

import os
import sys
import fsquery
from subprocess import check_output

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: %s path search extensions " % os.path.basename(__file__))
        sys.exit(1)
    ret = fsquery.makecontentlist(sys.argv[1], True, True, False, False, False, sys.argv[3:])
    for r in ret:
        try:
            out = check_output(["ag", sys.argv[2], r])
        except OSError as oe:
            print("Failed calling ag. Make sure silversearcher-ag is installed.")
            exit(1)
        if not len(out):
            continue
        print("\033[94m%s" % r)
        print("\033[0m%s" % out)

