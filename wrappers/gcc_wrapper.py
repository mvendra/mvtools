#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def exec(options_list, cwd = None):

    if not isinstance(options_list, list):
        return False, "options_list must be a list"

    full_cmd = ["gcc"]
    for opt in options_list:
        full_cmd.append(opt)

    v, r = generic_run.run_cmd_simple(full_cmd, use_cwd=cwd)
    if not v:
        return False, "Failed running gcc command: [%s]" % r

    return True, None

def puaq(selfhelp):
    print("Usage: %s [options-list]" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq(False)

    options_list = sys.argv[1:]

    v, r = exec(options_list)
    if not v:
        print(r)
        sys.exit(1)
