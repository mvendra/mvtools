#!/usr/bin/env python3

import sys
import os

import generic_run
import path_utils

def configure_and_generate(cmake_path, suppress_cmake_output, source_path, output_path, generator_type, options):

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

    return generic_run.run_cmd_simple(full_cmd, suppress_cmake_output, use_cwd=output_path)

def puaq():
    print("Hello from %s" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":
    puaq()
