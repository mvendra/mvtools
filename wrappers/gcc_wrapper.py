#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def exec(compiler_base, options_list, cwd = None):

    if not isinstance(options_list, list):
        return False, "options_list must be a list"

    compiler_path = "gcc"
    if compiler_base is not None:
        if not isinstance(compiler_base, str):
            return False, "compiler_base, when present, must be a string"
        compiler_path = path_utils.concat_path(compiler_base, "bin", compiler_path)

    full_cmd = [compiler_path]

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
