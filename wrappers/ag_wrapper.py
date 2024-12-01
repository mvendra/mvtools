#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def silversearch(target_path, pattern):

    target_path_filtered = path_utils.filter_remove_trailing_sep(target_path)

    if not os.path.exists(target_path_filtered):
        return False, "Target path [%s] does not exist." % target_path_filtered

    if os.path.isdir(target_path_filtered):
        return False, "Target path [%s] is a directory." % target_path_filtered

    v, r = generic_run.run_cmd(["ag", pattern, target_path])
    if not v:
        if isinstance(r, generic_run.run_cmd_result):
            # ag returns failed process if the pattern is not found
            return True, ""
        else:
            return False, "Could not launch ag process. Is the silversearcher installed?"

    return v, r.stdout

def puaq():
    print("Usage: %s target_path pattern" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    target_path = sys.argv[1]
    pattern = sys.argv[2]

    v, r = silversearch(target_path, pattern)
    if (r != ""):
        print(r)
    if not v:
        sys.exit(1)
