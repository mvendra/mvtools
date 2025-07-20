#!/usr/bin/env python3

import os

import path_utils
import mvtools_envvars

def makeAndGetTestFolder(additional_folder):

    v, r = mvtools_envvars.mvtools_envvar_read_temp_path()
    if not v:
        return False, r
    temp_dir = r

    if not os.path.exists(temp_dir):
        return False, "Test/temporary folder [%s] doesn't exist. Can't proceed." % temp_dir

    # general layer for git_visitor tests
    test_dir_pre = path_utils.concat_path(temp_dir, "mvtools_tests")
    if os.path.exists(test_dir_pre):
        return False, "[%s] already exists. Can't proceed." % test_dir_pre
    os.mkdir(test_dir_pre)

    # optionally add another layer (specific layer for each test case)
    final_dir = test_dir_pre
    if additional_folder is not None:
        final_dir = path_utils.concat_path(test_dir_pre, additional_folder)
        os.mkdir(final_dir)

    return True, (test_dir_pre, final_dir)

def throwsExcept1(ex_type, trigger, param1):

    try:
        trigger(param1)
    except ex_type as ex:
        return True
    return False

def throwsExcept2(ex_type, trigger, param1, param2):

    try:
        trigger(param1, param2)
    except ex_type as ex:
        return True
    return False
