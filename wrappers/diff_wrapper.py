#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def do_diff(left_path, right_path):

    left_path_res = os.path.abspath(left_path)
    right_path_res = os.path.abspath(right_path)
    left_path_res = path_utils.filter_remove_trailing_sep(left_path_res)
    right_path_res = path_utils.filter_remove_trailing_sep(right_path_res)

    if not os.path.exists(left_path_res):
        return False, "[%s] does not exist." % left_path_res

    if not os.path.exists(right_path_res):
        return False, "[%s] does not exist." % right_path_res

    if os.path.isdir(left_path_res):
        return False, "[%s] is a folder." % left_path_res

    if os.path.isdir(right_path_res):
        return False, "[%s] is a folder." % right_path_res

    v, r = generic_run.run_cmd(["diff", left_path_res, right_path_res])
    if not v:
        return False, "Failed running diff command: [%s]" % r

    if r.returncode == 2:
        return False, "Failed running diff command: [%s][%s]" % (r.stdout, r.stderr)

    return True, r.stdout

def puaq():
    print("Usage: %s left_path right_path" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    left_path = sys.argv[1]
    right_path = sys.argv[2]

    v, r = do_diff(left_path, right_path)
    if v:
        print(r)
    else:
        print("Failed calling diff on [%s][%s]: [%s]." % (left_path, right_path, r))
        sys.exit(1)
