#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def exec(args, cwd=None):

    if not isinstance(args, list):
        return False, "args must be a list"

    full_cmd = ["python3"]

    for a in args:
        full_cmd.append(a)

    v = None
    r = None

    if cwd is not None:
        v, r = generic_run.run_cmd(full_cmd, use_cwd=cwd)
    else:
        v, r = generic_run.run_cmd(full_cmd)

    if not v:
        return False, r
    return True, (r.success, r.stdout, r.stderr)

def puaq():
    print("Hello from %s" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":
    puaq()
