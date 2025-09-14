#!/usr/bin/env python

import sys
import os

import path_utils
import miniparse
import terminal_colors
import codelint

def check_leftover_state(source, name):

    if source:
        print("Switch [%s] was left unfinished" % name)
        sys.exit(codelint.CODELINT_CMDLINE_RETURN_ERROR)

def check_undefined_required(source, name):

    if source is None:
        print("Switch [%s] was left undefined" % name)
        sys.exit(codelint.CODELINT_CMDLINE_RETURN_ERROR)

def process_target(storage, source, exts):

    if os.path.isdir(source):
        v, r = codelint.files_from_folder(source, exts)
        if not v:
            return False, r
        storage += r
    else:
        storage.append(source)

    return True, None

def puaq(selfhelp): # print usage and quit
    print("Usage: %s [--help] [--min index] [--max index] [--ext extension] [--target file/folder] [--left pattern] [--right pattern]" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(codelint.CODELINT_CMDLINE_RETURN_ERROR)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq(False)

    min_str = None
    max_str = None
    min_next = False
    max_next = False

    ext = None
    files = []
    ext_next = False
    target = []
    target_next = False

    left = None
    right = None
    left_next = False
    right_next = False

    for p in sys.argv[1:]:

        # states
        if min_next:
            min_next = False
            min_str = p
            continue

        elif max_next:
            max_next = False
            max_str = p
            continue

        elif ext_next:
            ext_next = False
            if ext is None:
                ext = []
            ext.append(p)
            continue

        elif target_next:
            target_next = False
            target.append(p)
            continue

        elif left_next:
            left_next = False
            left = p
            continue

        elif right_next:
            right_next = False
            right = p
            continue

        # switches
        if p == "--help":
            puaq(True)

        elif p == "--min":
            min_next = True
            continue

        elif p == "--max":
            max_next = True
            continue

        elif p == "--ext":
            ext_next = True
            continue

        elif p == "--target":
            target_next = True
            continue

        elif p == "--left":
            left_next = True
            continue

        elif p == "--right":
            right_next = True
            continue

    check_leftover_state(min_next, "--min")
    check_leftover_state(max_next, "--max")
    check_leftover_state(ext_next, "--ext")
    check_leftover_state(target_next, "--target")
    check_leftover_state(left_next, "--left")
    check_leftover_state(right_next, "--right")

    check_undefined_required(left, "--left")
    check_undefined_required(right, "--right")

    for t in target:
        v, r = process_target(files, t, ext)
        if not v:
            print(r)
            sys.exit(codelint.CODELINT_CMDLINE_RETURN_ERROR)

    plugin_params = {}
    filters = {}

    plugin_params["lint-func-indexer-param-left"] = [left]
    plugin_params["lint-func-indexer-param-right"] = [right]

    if min_str is not None:
        filters["min-line"] = [min_str]

    if max_str is not None:
        filters["max-line"] = [max_str]

    v, r = codelint.codelint(["lint-func-indexer"], plugin_params, filters, True, True, files)
    if not v:
        print("%s%s%s" % (terminal_colors.TTY_RED, r[0], terminal_colors.get_standard_color()))
        if len(r[1]) > 0:
            print("\n%sPartially generated report:%s\n" % (terminal_colors.TTY_RED_BOLD, terminal_colors.get_standard_color()))
            codelint.print_report(r[1])
        sys.exit(codelint.CODELINT_CMDLINE_RETURN_ERROR)

    any_findings = False
    for e in r:
        if e[0]:
            any_findings = True
            print(e[1])

    if any_findings:
        sys.exit(codelint.CODELINT_CMDLINE_RETURN_PLUGIN_FINDING)
