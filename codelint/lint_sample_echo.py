#!/usr/bin/env python3

import sys
import os

import path_utils

def lint_name():
    return path_utils.basename_filtered(__file__)

def lint_pre(autocorrect, filename, shared_state, num_lines):

    print("mvdebug plugin1: [%s][%s][%s][%s]\n\n" % (autocorrect, filename, shared_state, num_lines))

def lint_cycle(autocorrect, filename, shared_state, line_index, content_line):

    # mvtodo: and how do we integrate autocorrect-generated changes? probably should let the engine (codelint) itself do that, based off of what we return from here

    print("mvdebug plugin2: [%s][%s][%s][%s][%s]\n" % (autocorrect, filename, shared_state, line_index, content_line))

def lint_post(autocorrect, filename, shared_state):

    print("mvdebug plugin3: [%s][%s][%s]\n\n" % (autocorrect, filename, shared_state))

def puaq():
    print("Usage: %s params" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()
    print("elo")
