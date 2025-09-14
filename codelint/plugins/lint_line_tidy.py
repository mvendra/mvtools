#!/usr/bin/env python

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

    msg_indent = None
    msg_trail = None
    result_return = None

    for c in content_line_local:
        if c != " ":
            break
        indent_counter += 1
        if indent_counter == indent_ratio:
            indent_counter = 0

    if indent_counter > 0:
        msg_indent = "bad indentation detected"

    if content_line_local.endswith(" "):
        msg_trail = "trailing spaces detected"

    if (msg_indent is not None) or (msg_trail is not None): # either

        patches_ret = []
        inbetween_str = ""
        local_first = ""
        local_second = ""

        if (msg_indent is not None) and (msg_trail is not None): # both
            inbetween_str = ". "
            local_first = msg_indent
            local_second = msg_trail
            patches_ret.append((line_index, content_line.rstrip()))

        else: # only one of either
            if msg_indent is not None:
                local_first = msg_indent
            if msg_trail is not None:
                local_second = msg_trail
                patches_ret.append((line_index, content_line.rstrip()))

        composed_msg = "%s%s%s" % (local_first, inbetween_str, local_second)
        final_msg = "[%s:%s]: %s." % (filename, line_index, composed_msg)
        result_return = (final_msg, patches_ret)

    return True, result_return

def lint_post(plugins_params, filename, shared_state):

    return True, None
