#!/usr/bin/env python3

import sys
import os

import path_utils
import string_utils

def lint_name():
    return path_utils.basename_filtered(__file__)

def lint_desc():
    return "checks whether the given patterns, if/when found, are found at the beginning of the source content"

def lint_pre(plugins_params, filename, shared_state, num_lines):

    if not "lint-if-has-then-must-be-start-pattern" in plugins_params:
        return False, "required parameter {lint-if-has-then-must-be-start-pattern} was not provided"

    for p in plugins_params["lint-if-has-then-must-be-start-pattern"]:
        if len(p) < 1:
            return False, "parameters from {lint-if-has-then-must-be-start-pattern} cannot be empty"

    return True, None

def lint_cycle(plugins_params, filename, shared_state, line_index, content_line):

    content_line_local = content_line

    if len(content_line_local) == 0:
        return True, None

    for p in plugins_params["lint-if-has-then-must-be-start-pattern"]:
        if p in content_line_local:
            if not content_line_local.startswith(p):
                ret_msg = "[%s:%s]: line [%s] has the pattern [%s] - but not at the beginning." % (filename, line_index, content_line_local, p)
                return True, (ret_msg, [])

    return True, None

def lint_post(plugins_params, filename, shared_state):

    return True, None
