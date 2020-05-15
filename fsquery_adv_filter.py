#!/usr/bin/env python3

import sys
import os

import path_utils
import detect_repo_type

def filter_is_last_not_equal_to(path, params):
    if path_utils.basename_filtered(path) != params:
        return True
    return False

def filter_is_last_equal_to(path, params):
    if path_utils.basename_filtered(path) == params:
        return True
    return False

def filter_is_repo(path, params):
    v, r = detect_repo_type.detect_repo_type(path)
    return v

def filter_path_list(path_list, filter_functions):

    if not isinstance(path_list, list):
        return None

    if not isinstance(filter_functions, list):
        return None

    for f in filter_functions:
        if not isinstance(f, tuple):
            return None
        if not len(f) == 2:
            return None

    return_list = []

    for p in path_list:

        all_filters_ok = True
        for f in filter_functions:

            func, params = f
            if not func(p, params):
                all_filters_ok = False

        if all_filters_ok:
            return_list.append(p)

    return return_list

def puaq():
    print("Hello from %s" % os.path.basename(__file__))

if __name__ == "__main__":
    puaq()
