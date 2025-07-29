#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def extract_options(cmake_path, source_path, temp_path):

    if not os.path.exists(source_path):
        return False, "Source path [%s] does not exist." % source_path

    if os.path.exists(temp_path):
        return False, "Temp path [%s] already exists." % temp_path

    os.mkdir(temp_path)

    if cmake_path is None:
        cmake_path = "cmake" # use whichever cmake is in the user's path

    full_cmd = [cmake_path]
    full_cmd.append(source_path)
    full_cmd.append("-LAH")

    v, r = generic_run.run_cmd(full_cmd, use_cwd=temp_path)
    if not v:
        return False, "Failed running cmake extract-options command: [%s][%s]" % (r.stdout, r.stderr)
    return True, (r.success, r.stdout, r.stderr)

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
        return False, "Failed running cmake configure-and-generate command: [%s][%s]" % (r.stdout, r.stderr)
    return True, (r.success, r.stdout, r.stderr)

def puaq(selfhelp):
    print("Hello from %s" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    puaq(False)
