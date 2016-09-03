#!/usr/bin/env python

import os
import git_visitor_base
from subprocess import check_output
from subprocess import CalledProcessError

def visitor_status(repos, options):

    for r in repos:
        try:
            out = check_output(["git", "-C", r, "status", "-s"])
        except CalledProcessError as cpe:
            print("Git status returned error.")
            return False
        except OSError as oe:
            print("Failed calling git. Make sure it is installed.")
            return False
        if len(out) == 0:
            pass # clean HEAD
        else:
            print("%s is dirty." % r)

    return True

if __name__ == "__main__":
    r = git_visitor_base.do_visit(None, None, visitor_status)
    if False in r:
        sys.exit(1)

