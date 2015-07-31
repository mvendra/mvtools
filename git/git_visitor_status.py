#!/usr/bin/env python

import sys
import os
from subprocess import check_output

def puaq():
    print("Usage: %s base_path." % os.path.basename(__file))
    sys.exit(1)

def filter_git_only(thelist):
    ret = []
    for d in thelist:
        if os.path.basename(d) == ".git":
            ret.append(d)
    return ret

def run_visitor_status(list_repos):
    print(list_repos)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    basepath = sys.argv[1]
    if not os.path.exists(basepath):
        print("%s does not exist. Aborting." % basepath)
        sys.exit(1)

    ret = fsquery.makecontentlist(basepath, True, False, False, False, True, []) # finds all .git
    ret = filter_git_only(ret)
    run_visitor_status(ret)

