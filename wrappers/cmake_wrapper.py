#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def configure_and_generate(cmake_path, source_path, output_path, generator_type, options):

    if options is None:
        return False, "Invalid options"

    if cmake_path is None:
        cmake_path = "cmake" # use whichever cmake is in the user's path

    options_cmdline = []
    # unfold options
    for k in options:
        options_cmdline.append("-D%s:%s=%s" % ( k, options[k][0], options[k][1] ))

    full_cmd = [cmake_path]
    full_cmd.append(source_path)
    full_cmd.append("-G")
    full_cmd.append(generator_type)
    full_cmd += options_cmdline

    v, r = generic_run.run_cmd(full_cmd, use_cwd=output_path)
    if not v:
        return False, r
    return True, (r.success, r.stdout, r.stderr)

def puaq():
    print("Hello from %s" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":
    puaq()
