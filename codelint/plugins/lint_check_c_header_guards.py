#!/usr/bin/env python3

import sys
import os

import path_utils

def lint_name():
    return path_utils.basename_filtered(__file__)

def lint_pre(plugins_params, filename, shared_state, num_lines):

    if "lint-check-c-header-guards-state" in shared_state:
        return False, "shared state already contains {lint-check-c-header-guards-state}"
    shared_state["lint-check-c-header-guards-state"] = "expecting-ifndef"

    return True, None

def lint_cycle(plugins_params, filename, shared_state, line_index, content_line):

    content_line_local = content_line.strip()

    if shared_state["lint-check-c-header-guards-state"] == "expecting-ifndef":

        if len(content_line_local) == 0:
            return True, None

        if content_line_local[0] == "#":
            content_line_local = content_line_local[1:]
            content_line_local = content_line_local.strip()
        else:
            return True, ("first content is not an ifndef (line [%s])" % line_index, [])

        if len(content_line_local) < 8: # "ifndef " + at least one more symbol
            return True, ("first content is not an ifndef (line [%s])" % line_index, [])

        if content_line_local[:6] == "ifndef":

            content_line_local = content_line_local[6:]
            content_line_local = content_line_local.strip()
            shared_state["lint-check-c-header-guards-first-ifndef-is"] = content_line_local
            shared_state["lint-check-c-header-guards-state"] = "expecting-define"
            return True, None

        return True, ("first content is not an ifndef (line [%s])" % line_index, [])

    elif shared_state["lint-check-c-header-guards-state"] == "expecting-define":

        if len(content_line_local) < 1:
            return True, ("follow-up define not found just after first ifndef (line [%s])" % line_index, [])

        if content_line_local[0] == "#":
            content_line_local = content_line_local[1:]
            content_line_local = content_line_local.strip()
        else:
            return True, ("follow-up define not found just after first ifndef (line [%s])" % line_index, [])

        if len(content_line_local) < 8: # "define " + at least one more symbol
            return True, ("follow-up define not found just after first ifndef (line [%s])" % line_index, [])

        if content_line_local[:6] == "define":

            content_line_local = content_line_local[6:]
            content_line_local = content_line_local.strip()
            if content_line_local != shared_state["lint-check-c-header-guards-first-ifndef-is"]:
                return True, ("incorrect header guard detected (line: [%s], expected: [%s], have: [%s])" % (line_index, shared_state["lint-check-c-header-guards-first-ifndef-is"], content_line_local), [])
            shared_state["lint-check-c-header-guards-state"] = "expecting-endif"
            return True, None

        return True, ("follow-up define not found just after first ifndef (line [%s])" % line_index, [])

    elif shared_state["lint-check-c-header-guards-state"] == "expecting-endif":

        if len(content_line_local) < 6:
            return True, None

        if content_line_local[:6] == "#endif":
            shared_state["lint-check-c-header-guards-last-endif"] = content_line_local

        return True, None

    return False, "unknown state"

def lint_post(plugins_params, filename, shared_state):

    if shared_state["lint-check-c-header-guards-state"] != "expecting-endif":
        return False, "wrong state at post"

    if not "lint-check-c-header-guards-last-endif" in shared_state:
        return True, ("no endifs detected", [])

    last_endif_local = shared_state["lint-check-c-header-guards-last-endif"]

    if len(last_endif_local) < 1:
        return True, ("invalid final endif", [])

    if last_endif_local[0] == "#":
        last_endif_local = last_endif_local[1:]
        last_endif_local = last_endif_local.strip()
    else:
        return True, ("invalid final endif", [])

    if len(last_endif_local) < 7: # "endif " + at least one more symbol
        return True, ("invalid final endif", [])

    if last_endif_local[:5] == "endif":
        last_endif_local = last_endif_local[5:]
        last_endif_local = last_endif_local.strip()
    else:
        return True, ("invalid final endif", [])

    if len(last_endif_local) < 4: # "// " + at least one more symbol
        return True, ("invalid final endif", [])

    if last_endif_local[:2] == "//":
        last_endif_local = last_endif_local[2:]
        last_endif_local = last_endif_local.strip()
    else:
        return True, ("invalid final endif", [])

    if last_endif_local != shared_state["lint-check-c-header-guards-first-ifndef-is"]:
        return True, ("incorrect header guard detected (at the final endif) - expected [%s], have [%s]" % (shared_state["lint-check-c-header-guards-first-ifndef-is"], last_endif_local), [])

    return True, None
