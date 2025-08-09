#!/usr/bin/env python3

import sys
import os

import path_utils
import miniparse
import terminal_colors
import codelint

COLOR_TABLE = {}
COLOR_TABLE[0] = terminal_colors.TTY_YELLOW
COLOR_TABLE[1] = terminal_colors.TTY_GREEN
COLOR_TABLE[2] = terminal_colors.TTY_BLUE
COLOR_TABLE[3] = terminal_colors.TTY_PURPLE
COLOR_TABLE[4] = terminal_colors.TTY_CYAN

def check_leftover_state(source, name):

    if source:
        print("Switch [%s] was left unfinished" % name)
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

def print_color_patterns(line, has_patterns):

    line_local = line
    line_result = ""
    pattern_countdown = 0

    for i in range(len(line_local)):

        if pattern_countdown > 0:
            pattern_countdown -= 1
            if pattern_countdown == 0:
                line_result += terminal_colors.get_standard_color()

        largest = miniparse.scan_largest_of(line_local, i, has_patterns)
        if largest is not None:

            pattern = has_patterns[largest]
            selected_color = COLOR_TABLE[largest % len(COLOR_TABLE)]
            line_result += selected_color
            pattern_countdown = len(pattern)

        line_result += line_local[i]

    print(line_result)

def puaq(selfhelp): # print usage and quit
    print("Usage: %s [--help] [--color] [--skip_non_utf8] [--min index] [--max index] [--ext extension] [--target file/folder] [--has pattern] [--not pattern] [--has-these [patterns] | --not-these [patterns]]" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(codelint.CODELINT_CMDLINE_RETURN_ERROR)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq(False)

    color = False
    skip_non_utf8 = False
    min_str = None
    max_str = None
    min_next = False
    max_next = False

    ext = None
    files = []
    ext_next = False
    target = []
    target_next = False

    has_list = []
    not_list = []
    has_next = False
    not_next = False
    has_these_next = False
    not_these_next = False

    for p in sys.argv[1:]:

        # continuous states
        if has_these_next:
            has_list.append(p)
            continue
        elif not_these_next:
            not_list.append(p)
            continue

        # repeatable states
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

        elif has_next:
            has_next = False
            has_list.append(p)
            continue

        elif not_next:
            not_next = False
            not_list.append(p)
            continue

        # switches
        if p == "--help":
            puaq(True)

        elif p == "--color":
            color = True
            continue

        elif p == "--skip_non_utf8":
            skip_non_utf8 = True
            continue

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

        elif p == "--has":
            has_next = True
            continue

        elif p == "--not":
            not_next = True
            continue

        elif p == "--has-these":
            has_these_next = True
            continue

        elif p == "--not-these":
            not_these_next = True
            continue

    check_leftover_state(min_next, "--min")
    check_leftover_state(max_next, "--max")
    check_leftover_state(ext_next, "--ext")
    check_leftover_state(target_next, "--target")
    check_leftover_state(has_next, "--has")
    check_leftover_state(not_next, "--not")

    for t in target:
        v, r = process_target(files, t, ext)
        if not v:
            print(r)
            sys.exit(codelint.CODELINT_CMDLINE_RETURN_ERROR)

    plugin_params = {}
    filters = {}

    plugin_params["lint-select-filter-include"] = has_list
    plugin_params["lint-select-filter-exclude"] = not_list

    if min_str is not None:
        filters["min-line"] = [min_str]

    if max_str is not None:
        filters["max-line"] = [max_str]

    v, r = codelint.codelint(["lint-select-filter"], plugin_params, filters, False, skip_non_utf8, files)
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
            if color:
                print_color_patterns(e[1], has_list)
            else:
                print(e[1])

    if any_findings:
        sys.exit(codelint.CODELINT_CMDLINE_RETURN_PLUGIN_FINDING)
