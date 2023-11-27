#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def move(source_path, target_path):

    if source_path is None:
        return False, "source_path is required"

    if target_path is None:
        return False, "target_path is required"

    source_path = os.path.abspath(source_path)
    target_path = os.path.abspath(target_path)

    full_cmd = ["mv", source_path, target_path]

    v, r = generic_run.run_cmd(full_cmd)
    if not v:
        return False, r
    return True, (r.success, r.stdout, r.stderr)

def puaq():
    print("Hello from %s" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":
    puaq()
