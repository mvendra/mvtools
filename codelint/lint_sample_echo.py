#!/usr/bin/env python3

import sys
import os

import path_utils

def lint_name():
    return path_utils.basename_filtered(__file__)

def lint_pre(plugins_params, autocorrect, filename, shared_state, num_lines):

    print("%s    (pre): [%s][%s][%s][%s][%s]" % (lint_name(), plugins_params, autocorrect, filename, shared_state, num_lines))
    return True, None

def lint_cycle(plugins_params, autocorrect, filename, shared_state, line_index, content_line):

    print("%s  (cycle): [%s][%s][%s][%s][%s][%s]" % (lint_name(), plugins_params, autocorrect, filename, shared_state, line_index, content_line))

    try:
        pattern_match = plugins_params["lint-sample-echo-pattern-match"]
    except KeyError as ex:
        return True, None

    for ps in pattern_match:
        if (ps in content_line):
            return True, ("detected pattern [%s] at line [%d]" % (ps, line_index), [])

    return True, None

def lint_post(plugins_params, autocorrect, filename, shared_state):

    print("%s   (post): [%s][%s][%s][%s]\n" % (lint_name(), plugins_params, autocorrect, filename, shared_state))
    return True, None

def puaq():
    print("Usage: %s params" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()
    print("elo")
