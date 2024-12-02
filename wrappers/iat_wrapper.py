#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def convert_to_iso(input_file, output_file):

    input_file_filtered = path_utils.filter_remove_trailing_sep(input_file)
    output_file_filtered = path_utils.filter_remove_trailing_sep(output_file)

    if not os.path.exists(input_file_filtered):
        return False, "Input file [%s] does not exist." % input_file_filtered

    if os.path.exists(output_file_filtered):
        return False, "Output file [%s] already exists." % output_file_filtered

    full_cmd = ["iat", "--iso", "-i", input_file_filtered, "-o", output_file_filtered]
    v, r = generic_run.run_cmd_simple(full_cmd)
    if not v:
        return False, "Failed iso-converting [%s] to [%s]: [%s]" % (input_file_filtered, output_file_filtered, r)

    return True, None

if __name__ == "__main__":
    print("Hello from %s" % path_utils.basename_filtered(__file__))
