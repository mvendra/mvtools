#!/usr/bin/env python

import sys
import os

import path_utils
import generic_run

def _unfold_options(input_options):

    options_list = []
    for k in input_options:
        options_list.append("-D%s:%s=%s" % ( k, input_options[k][0], input_options[k][1] ))
    return options_list

def extract_options(cmake_path, source_path, temp_path, options):

    if cmake_path is None:
        cmake_path = "cmake" # use whichever cmake is in the user's path

    if not os.path.exists(source_path):
        return False, "Source path [%s] does not exist." % source_path

    if os.path.exists(temp_path):
        return False, "Temp path [%s] already exists." % temp_path

    if options is None:
        return False, "Invalid options"

    os.mkdir(temp_path)

    options_cmdline = _unfold_options(options)

    full_cmd = [cmake_path]
    full_cmd.append(source_path)
    full_cmd.append("-LAH")
    full_cmd += options_cmdline

    v, r = generic_run.run_cmd(full_cmd, use_cwd=temp_path)
    if not v:
        return False, "Failed running cmake extract-options command: [%s][%s]" % (r.stdout, r.stderr)
    return True, (r.success, r.stdout, r.stderr)

def configure_and_generate(cmake_path, source_path, output_path, generator_type, options):

    if cmake_path is None:
        cmake_path = "cmake" # use whichever cmake is in the user's path

    if options is None:
        return False, "Invalid options"

    options_cmdline = _unfold_options(options)

    full_cmd = [cmake_path]
    full_cmd.append(source_path)
    full_cmd.append("-G")
    full_cmd.append(generator_type)
    full_cmd += options_cmdline

    v, r = generic_run.run_cmd(full_cmd, use_cwd=output_path)
    if not v:
        return False, "Failed running cmake configure-and-generate command: [%s][%s]" % (r.stdout, r.stderr)
    return True, (r.success, r.stdout, r.stderr)

def build(cmake_path, target_path, parallel):

    if cmake_path is None:
        cmake_path = "cmake" # use whichever cmake is in the user's path

    if not os.path.exists(target_path):
        return False, "Target path [%s] does not exist." % target_path

    full_cmd = [cmake_path]
    full_cmd.append("--build")
    full_cmd.append(target_path)
    if parallel:
        full_cmd.append("--parallel")

    v, r = generic_run.run_cmd(full_cmd)
    if not v:
        return False, "Failed running cmake build command: [%s][%s]" % (r.stdout, r.stderr)
    return True, (r.success, r.stdout, r.stderr)

def install(cmake_path, target_path, prefix):

    if cmake_path is None:
        cmake_path = "cmake" # use whichever cmake is in the user's path

    if not os.path.exists(target_path):
        return False, "Target path [%s] does not exist." % target_path

    full_cmd = [cmake_path]
    full_cmd.append("--install")
    full_cmd.append(target_path)

    if prefix is not None:
        if not os.path.exists(prefix):
            return False, "Prefix (path) [%s] does not exist." % prefix
        full_cmd.append("--prefix")
        full_cmd.append(prefix)

    v, r = generic_run.run_cmd(full_cmd)
    if not v:
        return False, "Failed running cmake install command: [%s][%s]" % (r.stdout, r.stderr)
    return True, (r.success, r.stdout, r.stderr)

def puaq(selfhelp):
    print("Hello from %s" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    puaq(False)
