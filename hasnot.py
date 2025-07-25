#!/usr/bin/env python3

import sys
import os

import path_utils
import terminal_colors
import fsquery
import codelint
import lint_select_filter

def puaq():
    print("Usage: %s [--has [patterns]] [--not [patterns]] [--files [targets] | --folder target [extensions] | (omitted -> cwd will be used with all extensions)] [--help]" % path_utils.basename_filtered(__file__))
    sys.exit(codelint.CODELINT_CMDLINE_RETURN_ERROR)

if __name__ == "__main__":

    if "--help" in sys.argv[1:]:
        puaq()

    if len(sys.argv) < 2:
        puaq()

    has_list = []
    not_list = []
    has_next = False
    not_next = False

    files = []
    files_next = False
    folder_next = False

    idx = 0
    for p in sys.argv[1:]:
        idx += 1

        if p == "--has":
            if (idx+1) == len(sys.argv):
                print("--has requires parameters")
                sys.exit(codelint.CODELINT_CMDLINE_RETURN_ERROR)
            has_next = True
            not_next = False
            continue
        elif p == "--not":
            if (idx+1) == len(sys.argv):
                print("--not requires parameters")
                sys.exit(codelint.CODELINT_CMDLINE_RETURN_ERROR)
            has_next = False
            not_next = True
            continue
        elif p == "--files":
            files_next = True
            break
        elif p == "--folder":
            folder_next = True
            break

        if has_next:
            has_list.append(p)
            continue

        if not_next:
            not_list.append(p)
            continue

    if files_next:

        if not len(sys.argv) > (idx+1):
            print("--files chosen but no target files were provided")
            sys.exit(codelint.CODELINT_CMDLINE_RETURN_ERROR)
        files = sys.argv[idx+1:]

    elif folder_next:

        if not len(sys.argv) > (idx+1):
            print("--folder chosen but no target folder was provided")
            sys.exit(codelint.CODELINT_CMDLINE_RETURN_ERROR)
        folder = sys.argv[idx+1]

        extensions = None
        if len(sys.argv) > (idx+2):
            extensions = sys.argv[idx+2:]

        v, r = fsquery.makecontentlist(folder, True, True, True, False, True, False, True, extensions)
        if not v:
            print(r)
            sys.exit(codelint.CODELINT_CMDLINE_RETURN_ERROR)
        files = r

    else:

        v, r = fsquery.makecontentlist(os.getcwd(), True, True, True, False, True, False, True, None)
        if not v:
            print(r)
            sys.exit(codelint.CODELINT_CMDLINE_RETURN_ERROR)
        files = r

    plugin_params = {}
    plugin_params["lint-select-filter-include"] = has_list
    plugin_params["lint-select-filter-exclude"] = not_list

    v, r = codelint.codelint([lint_select_filter], plugin_params, False, files)
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
