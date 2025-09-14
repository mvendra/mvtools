#!/usr/bin/env python

import sys
import os

import path_utils

def lint_name():
    return path_utils.basename_filtered(__file__)

def lint_desc():
    return "internal ut helper's sidekick"

def lint_pre(plugins_params, filename, shared_state, num_lines):
    return True, None

def lint_cycle(plugins_params, filename, shared_state, line_index, content_line):

    cycle_pattern_match = None
    cycle_pattern_replace = None

    try:
        cycle_pattern_match = plugins_params["lint-test-helper-sidekick-cycle-pattern-match"]
        cycle_pattern_match = cycle_pattern_match[0]
    except KeyError as ex:
        return True, None

    try:
        cycle_pattern_replace = plugins_params["lint-test-helper-sidekick-cycle-pattern-replace"]
        cycle_pattern_replace = cycle_pattern_replace[0]
    except KeyError as ex:
        return True, None

    ppos = content_line.find(cycle_pattern_match)
    if ppos == -1:
        return True, None

    updated_line = content_line.replace(cycle_pattern_match, cycle_pattern_replace)
    return True, ("(sidekick) detected pattern [%s] at line [%d]" % (cycle_pattern_match, line_index), [(line_index, updated_line)])

def lint_post(plugins_params, filename, shared_state):
    return True, None
