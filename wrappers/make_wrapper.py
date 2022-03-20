#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def make(work_dir, target, prefix):

    full_cmd = ["make"]

    if target is not None:
        full_cmd.append(target)

    if prefix is not None:
        prefix_line = "PREFIX=%s" % prefix
        full_cmd.append(prefix_line)

    v, r = generic_run.run_cmd(full_cmd, use_cwd=work_dir)
    if not v:
        return False, r
    return True, (r.success, r.stdout, r.stderr)

def puaq():
    print("Hello from %s" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":
    puaq()
