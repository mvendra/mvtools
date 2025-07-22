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
    pre_verify_fn = None
    pre_write_to_shared_state = None

    try:
        pre_fail = plugins_params["lint-test-helper-pre-fail"]
    except KeyError as ex:
        pass

    if pre_fail is not None:
        return False, pre_fail

    try:
        pre_verify_fn = plugins_params["lint-test-helper-pre-verify-filename"]
    except KeyError as ex:
        pass

    if pre_verify_fn is not None:
        if filename != pre_verify_fn:
            return False, "trigger assert fail"

    try:
        pre_write_to_shared_state = plugins_params["lint-test-helper-pre-write-to-shared-state"]
    except KeyError as ex:
        pass

    if pre_write_to_shared_state is not None:
        shared_state["lint-test-helper-shared-state-verify"] = pre_write_to_shared_state

    return True, None

def lint_cycle(plugins_params, filename, shared_state, line_index, content_line):

    # returns:
    # True, None
    # True, ( "msg", [ (1, "replace-first-line-with-this"), (2, "replace-second-line-with-this") ] )
    # False, "error msg"

    cycle_fail = None
    cycle_verify_fn = None
    cycle_verify_shared_state_verify = None
    cycle_verify_shared_state = None
    pattern_match = None
    pattern_replace = None

    try:
        cycle_fail = plugins_params["lint-test-helper-cycle-fail"]
    except KeyError as ex:
        pass

    if cycle_fail is not None:
        return False, cycle_fail

    try:
        cycle_verify_fn = plugins_params["lint-test-helper-cycle-verify-filename"]
    except KeyError as ex:
        pass

    if cycle_verify_fn is not None:
        if filename != cycle_verify_fn:
            return False, "trigger assert fail"

    try:
        cycle_verify_shared_state_verify = shared_state["lint-test-helper-shared-state-verify"]
    except KeyError as ex:
        pass

    if cycle_verify_shared_state_verify is not None:
        try:
            cycle_verify_shared_state = plugins_params["lint-test-helper-cycle-verify-shared-state"]
        except KeyError as ex:
            return False, "trigger assert fail"
        if cycle_verify_shared_state_verify != cycle_verify_shared_state:
            return False, "trigger assert fail"

    try:
        pattern_match = plugins_params["lint-test-helper-cycle-pattern-match"]
    except KeyError as ex:
        return True, None

    try:
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
    post_verify_fn = None
    post_verify_shared_state_verify = None
    post_verify_shared_state = None

    try:
        post_fail = plugins_params["lint-test-helper-post-fail"]
    except KeyError as ex:
        pass

    if post_fail is not None:
        return False, post_fail

    try:
        post_verify_fn = plugins_params["lint-test-helper-post-verify-filename"]
    except KeyError as ex:
        pass

    if post_verify_fn is not None:
        if filename != post_verify_fn:
            return False, "trigger assert fail"

    try:
        post_verify_shared_state_verify = shared_state["lint-test-helper-shared-state-verify"]
    except KeyError as ex:
        pass

    if post_verify_shared_state_verify is not None:
        try:
            post_verify_shared_state = plugins_params["lint-test-helper-post-verify-shared-state"]
        except KeyError as ex:
            return False, "trigger assert fail"
        if post_verify_shared_state_verify != post_verify_shared_state:
            return False, "trigger assert fail"

    return True, None

def puaq():
    print("Usage: %s params" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()
    print("elo")
