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

    print("%s    (pre): [%s][%s][%s][%s]" % (lint_name(), plugins_params, filename, shared_state, num_lines))
    return True, None

def lint_cycle(plugins_params, filename, shared_state, line_index, content_line):

    # returns:
    # True, None
    # True, ( "msg", [ (1, "replace-first-line-with-this"), (2, "replace-second-line-with-this") ] )
    # False, "error msg"

    print("%s  (cycle): [%s][%s][%s][%s][%s]" % (lint_name(), plugins_params, filename, shared_state, line_index, content_line))

    try:
        pattern_match = plugins_params["lint-sample-echo-pattern-match"]
    except KeyError as ex:
        return True, None

    for ps in pattern_match:
        if ps in content_line:
            return True, ("[%s:%s]: detected pattern [%s]." % (filename, line_index, ps), [])

    return True, None

def lint_post(plugins_params, filename, shared_state):

    # returns:
    # True, None
    # True, ( "msg", [ (1, "replace-first-line-with-this"), (2, "replace-second-line-with-this") ] )
    # False, "error msg"

    print("%s   (post): [%s][%s][%s]\n" % (lint_name(), plugins_params, filename, shared_state))
    return True, None
