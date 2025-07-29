#!/usr/bin/env python3

import sys
import os

import path_utils
import string_utils

def lint_name():
    return path_utils.basename_filtered(__file__)

def lint_desc():
    return "detects trailing spaces"

def lint_pre(plugins_params, filename, shared_state, num_lines):

    return True, None

def lint_cycle(plugins_params, filename, shared_state, line_index, content_line):

    content_line_local = content_line

    if len(content_line_local) == 0:
        return True, None

    indent_ratio = 4
    indent_counter = 0

    for c in content_line_local:
        if c != " ":
            break
        indent_counter += 1
        if indent_counter == indent_ratio:
            indent_counter = 0

    if indent_counter > 0:
        return True, ("[%s:%s]: bad indentation detected." % (filename, line_index), [])

    # mvtodo: merge them two

    if content_line_local.endswith(" "):
        return True, ("[%s:%s]: trailing spaces detected." % (filename, line_index), [(line_index, content_line_local.rstrip())])

    return True, None

def lint_post(plugins_params, filename, shared_state):

    return True, None
