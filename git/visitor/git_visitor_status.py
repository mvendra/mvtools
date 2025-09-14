#!/usr/bin/env python

import sys
import os
import git_visitor_base
import git_lib

def visitor_status(repos, options):

    for repo in repos:

        v, r = git_lib.status_simple(repo)
        if not v:
            print("visitor-status failed: %s" % r)
            return False
        if len(r) != 0:
            print("%s is dirty." % repo)

    return True

if __name__ == "__main__":
    r = git_visitor_base.do_visit(None, None, visitor_status)
    if r is None:
        sys.exit(1)
    elif False in r:
        sys.exit(2)
