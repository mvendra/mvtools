#!/usr/bin/env python

import os
import git_visitor_base
from subprocess import check_output
from subprocess import CalledProcessError

def visitor_status(repos, options):
    for r in repos:
        try:
            out = check_output(["git", "-C", r, "status", "-s"])
        except:
            print("Failed calling git. Make sure it is installed.")
            exit(1)
        if len(out) == 0:
            pass # clean HEAD
        else:
            print("%s is dirty." % r)

if __name__ == "__main__":
    git_visitor_base.do_visit(None, None, visitor_status)

