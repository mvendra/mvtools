#!/usr/bin/env python3

import sys
import os

import path_utils
import getcontents
import create_and_write_file
import string_utils
import fsquery
import terminal_colors

# plugins
import lint_sample_echo
import lint_check_c_header_guards
import lint_func_indexer
import lint_end_space_detector
import lint_c_integer_suffix
import lint_select_filter

CODELINT_CMDLINE_RETURN_PLUGIN_FINDING = 1
CODELINT_CMDLINE_RETURN_ERROR = 2

def helper_validate_msgpatch_return(msg, patches):

    if not isinstance(msg, str):
        return False, "invalid result return: msg is not a str"

    if not isinstance(patches, list):
        return False, "invalid result return: patches is not a list"

    for e in patches:

        if not isinstance(e, tuple):
            return False, "invalid result return: patches entry is not a tuple"

        if not isinstance(e[0], int):
            return False, "invalid result return: patches entry, first tuple entry is not an int"

        if not isinstance(e[1], str):
            return False, "invalid result return: patches entry, second tuple entry is not a str"

    return True, None

def helper_apply_patches(lines, patches):

    for pe in patches:

        pidx = pe[0]
        pcnt = pe[1]

        if pidx > len(lines):
            return False, "patch index [%s] is out of bounds [%s]" % (pidx, len(lines))

        if pidx == 0:
            return False, "patch index is zero (invalid base)"
        pidx -= 1

        lines[pidx] = pcnt

    return True, None

def helper_process_result(result, report, autocorrect, lines_copy):

    if result is None:
        return True, None
    msg, patches = result

    v, r = helper_validate_msgpatch_return(msg, patches)
    if not v:
        return False, r

    report.append((True, msg))

    if autocorrect:
        v, r = helper_apply_patches(lines_copy, patches)
        if not v:
            return False, r

    return True, None

def codelint(plugins, plugins_params, autocorrect, files):

    report = []

    # preconds
    if not isinstance(autocorrect, bool):
        return False, ("autocorrect is not a bool", report)

    if not isinstance(plugins, list):
        return False, ("plugins is not a list", report)

    if not isinstance(files, list):
        return False, ("files is not a list", report)

    if len(plugins) < 1:
        return False, ("No plugins selected", report)

    if autocorrect and len(plugins) > 1:
        return False, ("Only one plugin is allowed to be executed with autocorrect turned on", report)

    if len(files) < 1:
        return False, ("No target files selected", report)

    for f in files:
        if not os.path.exists(f):
            return False, ("File [%s] does not exist" % f, report)
        if os.path.isdir(f):
            return False, ("File [%s] is a directory" % f, report)

    for f in files:

        shared_state = {}

        fn = path_utils.basename_filtered(f)
        contents = getcontents.getcontents(f)
        lines = contents.split("\n")
        lines_copy = None
        if autocorrect:
            lines_copy = lines.copy()

        report.append((False, "Processing [%s] - begin" % f))

        for p in plugins:

            report.append((False, "Plugin: [%s] - begin" % p.lint_name()))
            v, r = p.lint_pre(plugins_params, fn, shared_state, len(lines))
            if not v:
                return False, ("Plugin [%s] failed (pre): [%s]" % (p.lint_name(), r), report)

            idx = 0
            for l in lines:
                idx += 1

                v, r = p.lint_cycle(plugins_params, fn, shared_state, idx, l)
                if not v:
                    return False, ("Plugin [%s] failed (cycle): [%s]" % (p.lint_name(), r), report)

                v, r = helper_process_result(r, report, autocorrect, lines_copy)
                if not v:
                    return False, ("Plugin [%s] failed (cycle-result): [%s]" % (p.lint_name(), r), report)

            v, r = p.lint_post(plugins_params, fn, shared_state)
            if not v:
                return False, ("Plugin [%s] failed (post): [%s]" % (p.lint_name(), r), report)

            v, r = helper_process_result(r, report, autocorrect, lines_copy)
            if not v:
                return False, ("Plugin [%s] failed (post-result): [%s]" % (p.lint_name(), r), report)

            report.append((False, "Plugin: [%s] - end" % p.lint_name()))

        if autocorrect:
            os.unlink(f)
            create_and_write_file.create_file_contents(f, string_utils.line_list_to_string(lines_copy))
        report.append((False, "Processing [%s] - end" % f))

    return True, report

def print_report(report):

    any_findings = False
    for e in report:
        if e[0]:
            print("%s%s%s" % (terminal_colors.TTY_YELLOW, e[1], terminal_colors.TTY_WHITE))
            any_findings = True
        else:
            print(e[1])
    return any_findings

def applet_helper(plugins, plugins_params, autocorrect, files):

    v, r = codelint(plugins, plugins_params, autocorrect, files)
    if not v:
        print("%s%s%s" % (terminal_colors.TTY_RED, r[0], terminal_colors.TTY_WHITE))
        if len(r[1]) > 0:
            print("\n%sPartially generated report:%s\n" % (terminal_colors.TTY_RED_BOLD, terminal_colors.TTY_WHITE))
            print_report(r[1])
        sys.exit(CODELINT_CMDLINE_RETURN_ERROR)
    print("%sComplete report%s:\n" % (terminal_colors.TTY_WHITE_BOLD, terminal_colors.TTY_WHITE))
    if print_report(r):
        print("\n%sAll operations suceeded - with some findings%s" % (terminal_colors.TTY_GREEN_BOLD, terminal_colors.TTY_WHITE))
        sys.exit(CODELINT_CMDLINE_RETURN_PLUGIN_FINDING)
    else:
        print("\n%sAll operations suceeded - no findings%s" % (terminal_colors.TTY_GREEN, terminal_colors.TTY_WHITE))

def puaq():
    print("Usage: %s [--plugin (see below)] [--plugin-param name value] [--autocorrect (only one plugin allowed per run)] [--files [targets] | --folder target [extensions]] [--help]" % path_utils.basename_filtered(__file__))
    print("Plugin list:")
    print("* lint-sample-echo {lint-sample-echo-pattern-match -> pattern}")
    print("* lint-check-c-header-guards {}")
    print("* lint-func-indexer {lint-func-indexer-param-left -> pattern / lint-func-indexer-param-right -> pattern}")
    print("* lint-end-space-detector {}")
    print("* lint-c-integer-suffix {lint-c-integer-suffix-warn-no-suffix}")
    print("* lint-select-filter {lint-select-filter-include -> [] / lint-select-filter-exclude -> []}")
    sys.exit(CODELINT_CMDLINE_RETURN_ERROR)

if __name__ == "__main__":

    if "--help" in sys.argv[1:]:
        puaq()

    if len(sys.argv) < 3:
        puaq()

    plugin_table = {}
    plugin_table["lint-sample-echo"] = lint_sample_echo
    plugin_table["lint-check-c-header-guards"] = lint_check_c_header_guards
    plugin_table["lint-func-indexer"] = lint_func_indexer
    plugin_table["lint-end-space-detector"] = lint_end_space_detector
    plugin_table["lint-c-integer-suffix"] = lint_c_integer_suffix
    plugin_table["lint-select-filter"] = lint_select_filter

    plugins = []
    plugins_params = {}
    autocorrect = False
    files = None
    folder = None
    extensions = None

    plugin_next = False
    plugin_param_name = None
    plugin_param_name_next = False
    plugin_param_value_next = False
    files_next = False
    folder_next = False

    idx = 0
    for p in sys.argv[1:]:
        idx += 1

        if folder_next:
            folder = p
            break

        if plugin_next:
            plugin_next = False
            if not p in plugin_table:
                print("Plugin [%s] does not exist" % p)
                sys.exit(CODELINT_CMDLINE_RETURN_ERROR)
            plugins.append(plugin_table[p])
            continue

        if plugin_param_value_next:
            plugin_param_value_next = False
            if plugin_param_name in plugins_params:
                plugins_params[plugin_param_name].append(p)
            else:
                plugins_params[plugin_param_name] = [p]
            plugin_param_name = None
            continue

        if plugin_param_name_next:
            plugin_param_name_next = False
            plugin_param_value_next = True
            plugin_param_name = p
            continue

        if p == "--plugin":
            plugin_next = True
        elif p == "--plugin-param":
            plugin_param_name_next = True
        elif p == "--autocorrect":
            autocorrect = True
        elif p == "--folder":
            folder_next = True
        elif p == "--files":
            files_next = True
            break

    if plugin_param_name_next:
        print("Missing plugin param name")
        sys.exit(CODELINT_CMDLINE_RETURN_ERROR)

    if plugin_param_value_next:
        print("Missing plugin param value (expected for [%s])" % plugin_param_name)
        sys.exit(CODELINT_CMDLINE_RETURN_ERROR)

    if files_next:
        files = sys.argv[idx+1:]
    elif folder_next:

        if len(sys.argv) > (idx+1):
            extensions = sys.argv[idx+1:]

        v, r = fsquery.makecontentlist(folder, True, True, True, False, True, False, True, extensions)
        if not v:
            print(r)
            sys.exit(CODELINT_CMDLINE_RETURN_ERROR)
        files = r

    else:
        print("Neither --files nor --folder chosen")
        sys.exit(CODELINT_CMDLINE_RETURN_ERROR)

    applet_helper(plugins, plugins_params, autocorrect, files)
