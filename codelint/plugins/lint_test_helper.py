#!/usr/bin/env python3

import sys
import os

import path_utils

def lint_name():
    return path_utils.basename_filtered(__file__)

def lint_pre(plugins_params, filename, shared_state, num_lines):

    # returns:
    # True, None
    # False, "error msg"

    pre_fail = None
    try:
        pre_fail = plugins_params["lint-test-helper-pre-fail"]
    except KeyError as ex:
        pass

    if pre_fail is not None:
        return False, pre_fail

    return True, None

def lint_cycle(plugins_params, filename, shared_state, line_index, content_line):

    # returns:
    # True, None
    # True, ( "msg", [ (1, "replace-first-line-with-this"), (2, "replace-second-line-with-this") ] )
    # False, "error msg"

    cycle_fail = None
    try:
        cycle_fail = plugins_params["lint-test-helper-cycle-fail"]
    except KeyError as ex:
        pass

    if cycle_fail is not None:
        return False, cycle_fail

    try:
        pattern_match = plugins_params["lint-test-helper-cycle-pattern-match"]
        pattern_replace = plugins_params["lint-test-helper-cycle-pattern-replace"]
    except KeyError as ex:
        return True, None

    ppos = content_line.find(pattern_match)
    if ppos == -1:
        return True, None

    updated_line = content_line.replace(pattern_match, pattern_replace)
    return True, ("detected pattern [%s] at line [%d]" % (pattern_match, line_index), [(line_index, updated_line)])

def lint_post(plugins_params, filename, shared_state):

    # returns:
    # True, None
    # True, ( "msg", [ (1, "replace-first-line-with-this"), (2, "replace-second-line-with-this") ] )
    # False, "error msg"

    post_fail = None
    try:
        post_fail = plugins_params["lint-test-helper-post-fail"]
    except KeyError as ex:
        pass

    if post_fail is not None:
        return False, post_fail

    return True, None

def puaq():
    print("Usage: %s params" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()
    print("elo")
