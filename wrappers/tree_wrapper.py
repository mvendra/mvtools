#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def make_tree(folder_to_tree):

    folder_to_tree = path_utils.filter_remove_trailing_sep(folder_to_tree)

    if not os.path.exists(folder_to_tree):
        return False, "%s does not exist." % folder_to_tree

    if not os.path.isdir(folder_to_tree):
        return False, "%s is not a directory." % folder_to_tree

    v, r = generic_run.run_cmd_simple(["tree", "-a", folder_to_tree])
    return v, r

def puaq():
    print("Usage: %s folder" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    target_path = sys.argv[1]

    v, r = make_tree(target_path)
    if v:
        print(r)
    else:
        print("Failed calling 'tree' on [%s]." % target_path)
        sys.exit(1)
