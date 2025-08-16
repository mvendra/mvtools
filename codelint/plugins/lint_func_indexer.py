#!/usr/bin/env python3

import sys
import os

import path_utils
import string_utils

def lint_name():
    return path_utils.basename_filtered(__file__)

def lint_desc():
    return "checks whether a proper indexing takes place inbetween two text patterns"

def lint_pre(plugins_params, filename, shared_state, num_lines):

    if "lint-func-indexer-counter" in shared_state:
        return False, "shared state already contains {lint-func-indexer-counter}"
    shared_state["lint-func-indexer-counter"] = 0

    if not "lint-func-indexer-param-left" in plugins_params:
        return False, "required parameter {lint-func-indexer-param-left} was not provided"

    if not "lint-func-indexer-param-right" in plugins_params:
        return False, "required parameter {lint-func-indexer-param-right} was not provided"

    if len(plugins_params["lint-func-indexer-param-left"]) != 1:
        return False, "the parameter {lint-func-indexer-param-left} must contain at least one entry"

    if len(plugins_params["lint-func-indexer-param-right"]) != 1:
        return False, "the parameter {lint-func-indexer-param-right} must contain at least one entry"

    if len(plugins_params["lint-func-indexer-param-left"][0]) < 1:
        return False, "the parameter {lint-func-indexer-param-left} cannot be empty"

    if len(plugins_params["lint-func-indexer-param-right"][0]) < 1:
        return False, "the parameter {lint-func-indexer-param-right} cannot be empty"

    return True, None

def lint_cycle(plugins_params, filename, shared_state, line_index, content_line):

    content_line_local = content_line

    if len(content_line_local) == 0:
        return True, None

    lp = None
    rp = None

    for p in plugins_params["lint-func-indexer-param-left"]:
        if lp is not None:
            if len(p) < len(lp):
                continue
        if content_line_local.startswith(p):
            lp = p

    for p in plugins_params["lint-func-indexer-param-right"]:
        if rp is not None:
            if len(p) < len(rp):
                continue
        if content_line_local.endswith(p):
            rp = p

    if (lp is None) or (rp is None):
        return True, None

    content_line_local = content_line_local[len(lp):] # remove left
    if len(content_line_local) <= len(rp):
        return True, None
    content_line_local = content_line_local[:len(content_line_local) - len(rp)] # remove right

    shared_state["lint-func-indexer-counter"] += 1

    logic_sieve = False
    if not string_utils.is_dec_string(content_line_local):
        logic_sieve = True
    elif not int(content_line_local) == shared_state["lint-func-indexer-counter"]:
        logic_sieve = True

    if logic_sieve:
        ret_msg = "[%s:%s]: expected index [%s], have [%s]." % (filename, line_index, shared_state["lint-func-indexer-counter"], content_line_local)
        corrected_line = "%s%s%s" % (lp, shared_state["lint-func-indexer-counter"], rp)
        return True, (ret_msg, [(line_index, corrected_line)])

    return True, None

def lint_post(plugins_params, filename, shared_state):

    return True, None
