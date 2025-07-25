#!/usr/bin/env python3

import sys
import os

import path_utils
import string_utils

def lint_name():
    return path_utils.basename_filtered(__file__)

def lint_pre(plugins_params, filename, shared_state, num_lines):

    patterns_inc = []
    if "lint-select-filter-include" in plugins_params:
        patterns_inc = plugins_params["lint-select-filter-include"]

    if len(patterns_inc) < 1:
        return False, "at least one entry is required for {lint-select-filter-include}"

    return True, None

def lint_cycle(plugins_params, filename, shared_state, line_index, content_line):

    content_line_local = content_line

    if len(content_line_local) == 0:
        return True, None

    patterns_inc = []
    patterns_exc = []

    if "lint-select-filter-include" in plugins_params:
        patterns_inc = plugins_params["lint-select-filter-include"]

    if "lint-select-filter-exclude" in plugins_params:
        patterns_exc = plugins_params["lint-select-filter-exclude"]

    for inc_f in patterns_inc:
        if content_line.find(inc_f) == -1:
            return True, None

    for exc_f in patterns_exc:
        if content_line.find(exc_f) > -1:
            return True, None

    return True, ("[%s:%s]: %s." % (filename, line_index, content_line), [])

def lint_post(plugins_params, filename, shared_state):

    return True, None
