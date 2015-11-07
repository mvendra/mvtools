#!/usr/bin/env python

import os
import git_visitor_base
from subprocess import check_output

def visitor_status(repos):
    for r in repos:
        out = check_output(["git", "--git-dir=%s" % r, "--work-tree=%s" % os.path.dirname(r), "status", "-s"])
        if len(out) == 0:
            pass # clean HEAD
        else:
            print("%s is dirty." % os.path.dirname(r))

if __name__ == "__main__":
    git_visitor_base.do_visit(None, visitor_status)

