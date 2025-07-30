#!/usr/bin/env python3

import sys
import os

import path_utils
import terminal_colors
import codelint

def puaq(selfhelp):
    print("Usage: %s [--help] [--min-line index] [--max-line index] [--ext extension] [--target file/folder] [--has pattern] [--not pattern] [--has-these [patterns] | --not-these [patterns]]" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(codelint.CODELINT_CMDLINE_RETURN_ERROR)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq(False)

    min_line = None
    max_line = None
    min_line_next = False
    max_line_next = False

    ext = None
    files = []
    ext_next = False
    target_next = False

    has_list = []
    not_list = []
    has_next = False
    not_next = False
    has_these_next = False
    not_these_next = False

    idx = 0
    for p in sys.argv[1:]:
        idx += 1

        if p == "--help":
            puaq(True)

    plugin_params = {}
    filters = {}

    plugin_params["lint-select-filter-include"] = has_list
    plugin_params["lint-select-filter-exclude"] = not_list

    print("mvdebug begin")
    print(min_line)
    print(max_line)
    print(ext)
    print(files)
    print(has_list)
    print(not_list)
    print(filters)
    print("mvdebug end")

    v, r = codelint.codelint(["lint-select-filter"], plugin_params, filters, False, files)
    if not v:
        print("%s%s%s" % (terminal_colors.TTY_RED, r[0], terminal_colors.TTY_WHITE))
        if len(r[1]) > 0:
            print("\n%sPartially generated report:%s\n" % (terminal_colors.TTY_RED_BOLD, terminal_colors.TTY_WHITE))
            codelint.print_report(r[1])
        sys.exit(codelint.CODELINT_CMDLINE_RETURN_ERROR)

    any_findings = False
    for e in r:
        if e[0]:
            any_findings = True
            print(e[1])

    if any_findings:
        sys.exit(codelint.CODELINT_CMDLINE_RETURN_PLUGIN_FINDING)
