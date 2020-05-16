#!/usr/bin/env python3

import sys
import os

import path_utils
import detect_repo_type

def filter_all_positive(path, params):
    return True

def filter_all_negative(path, params):
    return False

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

def and_adapter(predicate, func, path, params):
    r = func(path, params)
    if predicate is None:
        return r
    r &= predicate
    return r

def or_adapter(predicate, func, path, params):
    r = func(path, params)
    if predicate is None:
        return r
    r |= predicate
    return r

def filter_path_list_and(path_list, filter_functions):
    return filter_path_list(path_list, filter_functions, and_adapter)

def filter_path_list_or(path_list, filter_functions):
    return filter_path_list(path_list, filter_functions, or_adapter)

def filter_path_list(path_list, filter_functions, predicate_adapter):

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

        all_filters_ok = None
        for f in filter_functions:

            func, params = f
            all_filters_ok = predicate_adapter(all_filters_ok, func, p, params)

        if all_filters_ok:
            return_list.append(p)

    return return_list

def puaq():
    print("Hello from %s" % os.path.basename(__file__))

if __name__ == "__main__":
    puaq()
