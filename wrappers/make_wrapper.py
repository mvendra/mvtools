#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def make(work_dir, suppress_make_output, target):

    full_cmd = ["make"]

    if target is not None:
        full_cmd.append(target)

    return generic_run.run_cmd_simple(full_cmd, suppress_make_output, use_cwd=work_dir)

def puaq():
    print("Hello from %s" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":
    puaq()
