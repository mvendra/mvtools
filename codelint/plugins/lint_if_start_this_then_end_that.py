#!/usr/bin/env python

import sys
import os

import path_utils
import string_utils

def lint_name():
    return path_utils.basename_filtered(__file__)

def lint_desc():
    return "checks whether a given pattern, if/when found at the beginning of the source content, will have a corresponding specific given pattern at the end of the source content"

def lint_pre(plugins_params, filename, shared_state, num_lines):

    if not "lint-if-start-this-then-end-that-start-pattern" in plugins_params:
        return False, "required parameter {lint-if-start-this-then-end-that-start-pattern} was not provided"

    if not "lint-if-start-this-then-end-that-end-pattern" in plugins_params:
        return False, "required parameter {lint-if-start-this-then-end-that-end-pattern} was not provided"

    if len(plugins_params["lint-if-start-this-then-end-that-start-pattern"]) != 1:
        return False, "the parameter {lint-if-start-this-then-end-that-start-pattern} must contain one (and only) entry"

    if len(plugins_params["lint-if-start-this-then-end-that-end-pattern"]) != 1:
        return False, "the parameter {lint-if-start-this-then-end-that-end-pattern} must contain one (and only) entry"

    if len(plugins_params["lint-if-start-this-then-end-that-start-pattern"][0]) < 1:
        return False, "the parameter {lint-if-start-this-then-end-that-start-pattern} cannot be empty"

    if len(plugins_params["lint-if-start-this-then-end-that-end-pattern"][0]) < 1:
        return False, "the parameter {lint-if-start-this-then-end-that-end-pattern} cannot be empty"

    return True, None

def lint_cycle(plugins_params, filename, shared_state, line_index, content_line):

    content_line_local = content_line

    if len(content_line_local) == 0:
        return True, None

    sp = plugins_params["lint-if-start-this-then-end-that-start-pattern"][0]
    ep = plugins_params["lint-if-start-this-then-end-that-end-pattern"][0]

    tolerate = []
    try:
        tolerate = plugins_params["lint-if-start-this-then-end-that-tolerate"]
    except KeyError:
        pass

    if content_line_local.startswith(sp):
        if not content_line_local.endswith(ep):
            if not content_line_local in tolerate:
                ret_msg = "[%s:%s]: line [%s] has the pattern [%s] in the beginning - but not the pattern [%s] at the end." % (filename, line_index, content_line_local, sp, ep)
                return True, (ret_msg, [])

    return True, None

def lint_post(plugins_params, filename, shared_state):

    return True, None
