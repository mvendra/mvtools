#!/usr/bin/env python3

import sys
import os

import generic_run
import path_utils

def make(work_dir, target):

    full_cmd = ["make"]

    if target is not None:
        full_cmd.append(target)

    return generic_run.run_cmd_simple(full_cmd, use_cwd=work_dir)

def puaq():
    print("Hello from %s" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":
    puaq()
