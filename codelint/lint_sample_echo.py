#!/usr/bin/env python3

import sys
import os

import path_utils

def lint_name():
    return path_utils.basename_filtered(__file__)

def lint_pre(plugins_params, autocorrect, filename, shared_state, num_lines):

    print("mvdebug plugin1: [%s][%s][%s][%s][%s]\n\n" % (plugins_params, autocorrect, filename, shared_state, num_lines))
    return True, None

def lint_cycle(plugins_params, autocorrect, filename, shared_state, line_index, content_line):

    # mvtodo: and how do we integrate autocorrect-generated changes? probably should let the engine (codelint) itself do that, based off of what we return from here

    if (content_line == "some"):
        print("mvdebug plugin2: [%s][%s][%s][%s][%s][%s]\n" % (plugins_params, autocorrect, filename, shared_state, line_index, content_line))
        return True, ("detected some at line [%d]" % line_index, [])

    return True, None

def lint_post(plugins_params, autocorrect, filename, shared_state):

    print("mvdebug plugin3: [%s][%s][%s][%s]\n\n" % (plugins_params, autocorrect, filename, shared_state))
    return True, None

def puaq():
    print("Usage: %s params" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()
    print("elo")
