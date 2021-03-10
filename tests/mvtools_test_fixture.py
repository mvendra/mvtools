#!/usr/bin/env python3

import os
import path_utils

def makeAndGetTestFolder(additional_folder):

    nuke_dir = os.path.expanduser("~/nuke")
    # must have a $home/nuke folder, for creating test folders
    if not os.path.exists(nuke_dir):
        return False, "[%s] doesn't exist. Can't proceed." % nuke_dir

    # general layer for git_visitor tests
    test_dir_pre = path_utils.concat_path(nuke_dir, "mvtools_tests")
    if os.path.exists(test_dir_pre):
        return False, "[%s] already exists. Can't proceed." % test_dir_pre
    os.mkdir(test_dir_pre)

    # optionally add another layer (specific layer for each test case)
    final_dir = test_dir_pre
    if additional_folder is not None:
        final_dir = path_utils.concat_path(test_dir_pre, additional_folder)
        os.mkdir(final_dir)

    return True, (test_dir_pre, final_dir)
