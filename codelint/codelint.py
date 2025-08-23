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
import lint_func_indexer
import lint_c_integer_suffix
import lint_select_filter
import lint_c_check_header_guards
import lint_line_tidy
import lint_if_has_then_must_be_start
import lint_if_start_this_then_end_that

CODELINT_CMDLINE_RETURN_PLUGIN_FINDING = 1
CODELINT_CMDLINE_RETURN_ERROR = 2

plugin_table = {}
plugin_table["lint-sample-echo"] = (lint_sample_echo, "{lint-sample-echo-pattern-match -> pattern}")
plugin_table["lint-func-indexer"] = (lint_func_indexer, "{lint-func-indexer-param-left -> pattern / lint-func-indexer-param-right -> pattern}")
plugin_table["lint-c-integer-suffix"] = (lint_c_integer_suffix, "{lint-c-integer-suffix-warn-no-suffix}")
plugin_table["lint-select-filter"] = (lint_select_filter, "{lint-select-filter-include -> [patterns] / lint-select-filter-exclude -> [patterns]}")
plugin_table["lint-c-check-header-guards"] = (lint_c_check_header_guards, "{}")
plugin_table["lint-line-tidy"] = (lint_line_tidy, "{}")
plugin_table["lint-if-has-then-must-be-start"] = (lint_if_has_then_must_be_start, "{lint-if-has-then-must-be-start-pattern -> [patterns] / lint-if-has-then-must-be-start-tolerate-start -> [patterns]}")
plugin_table["lint-if-start-this-then-end-that"] = (lint_if_start_this_then_end_that, "{lint-if-start-this-then-end-that-start-pattern -> pattern / lint-if-start-this-then-end-that-end-pattern -> pattern / lint-if-start-this-then-end-that-tolerate -> [patterns]}")

filter_table = {}
filter_table["min-line"] = ("{index}", "skips lines below this index")
filter_table["max-line"] = ("{index}", "skips lines above this index")
filter_table["max-findings"] = ("{count}", "will stop linting if this limit is reached") # note that it's still possible for an execution to yield count+1 due to the lint_post() step being also able to return an additional finding

def resolve_plugin_name(plugin_name):

    if plugin_name in plugin_table:
        return plugin_table[plugin_name][0]
    return None

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

    return True, len(patches)

def helper_process_result(result, report, autocorrect, lines_copy):

    applied_patches = 0

    if result is None:
        return True, (0, applied_patches)
    msg, patches = result

    v, r = helper_validate_msgpatch_return(msg, patches)
    if not v:
        return False, r

    report.append((True, msg))

    if autocorrect:
        v, r = helper_apply_patches(lines_copy, patches)
        if not v:
            return False, r
        applied_patches = r

    return True, (1, applied_patches)

def helper_make_extra_plugin_end_str(num_findings, num_patches_applied):

    findings_str = ""
    patches_str = ""
    extra_str = ""
    inbetween_str = ""
    has_either = False
    has_both = False

    if num_findings > 0:
        has_either = True
        str_plural = ""
        if num_findings > 1:
            str_plural = "s"
        findings_str = "detected %s finding%s" % (num_findings, str_plural)

    if num_patches_applied > 0:
        if has_either:
            has_both = True
        else:
            has_either = True
        str_plural = ""
        if num_patches_applied > 1:
            str_plural = "es"
        patches_str = "applied %s patch%s" % (num_patches_applied, str_plural)

    if has_both:
        inbetween_str = ", "

    if has_either:
        extra_str = " (%s%s%s)" % (findings_str, inbetween_str, patches_str)
    return extra_str

def codelint(plugins, plugins_params, filters, autocorrect, skip_non_utf8, files):

    report = []

    # preconds
    if not isinstance(plugins, list):
        return False, ("plugins is not a list", report)

    if not isinstance(plugins_params, dict):
        return False, ("plugins_params is not a dict", report)

    for key in plugins_params:
        if not isinstance(plugins_params[key], list):
            return False, ("plugins_params[%s] is not a list" % key, report)
        for e in plugins_params[key]:
            if not isinstance(e, str):
                return False, ("plugins_params[%s]'s entry [%s] is not a string" % (key, e), report)

    if not isinstance(filters, dict):
        return False, ("filters is not a dict", report)

    for key in filters:
        if not isinstance(filters[key], list):
            return False, ("filters[%s] is not a list" % key, report)
        for e in filters[key]:
            if not isinstance(e, str):
                return False, ("filters[%s]'s entry [%s] is not a string" % (key, e), report)

    if not isinstance(autocorrect, bool):
        return False, ("autocorrect is not a bool", report)

    if not isinstance(skip_non_utf8, bool):
        return False, ("skip_non_utf8 is not a bool", report)

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

    plugins_resolved = []
    for p in plugins:
        p_mod = resolve_plugin_name(p)
        if p_mod is None:
            return False, ("Plugin [%s] does not exist" % p, report)
        plugins_resolved.append(p_mod)

    filter_min_line = 0
    filter_max_line = None
    filter_max_findings = None

    if "min-line" in filters:
        filter_min_line = int(filters["min-line"][0])
        if filter_min_line > 0:
            filter_min_line -= 1
    if "max-line" in filters:
        filter_max_line = int(filters["max-line"][0])
        if (filter_min_line+1) > filter_max_line:
            return False, ("min-line [%s] is larger than max-line [%s]" % (filter_min_line+1, filter_max_line), report)
    if "max-findings" in filters:
        filter_max_findings = int(filters["max-findings"][0])

    for f in files:

        shared_state = {}

        fn = path_utils.basename_filtered(f)
        try:
            contents = getcontents.getcontents(f)
        except UnicodeDecodeError as ex:
            if skip_non_utf8:
                report.append((False, "Skipped processing [%s] for being non-utf8" % f))
                continue
            return False, ("File [%s] is not UTF8 decodable" % f, report)
        lines = contents.split("\n")
        lines_copy = None
        if autocorrect:
            lines_copy = lines.copy()

        report.append((False, "Processing [%s] - begin" % f))

        num_findings = 0
        num_patches_applied = 0

        for p in plugins_resolved:

            report.append((False, "Plugin: [%s] - begin" % p.lint_name()))
            v, r = p.lint_pre(plugins_params, fn, shared_state, len(lines))
            if not v:
                return False, ("Plugin [%s] failed (pre): [%s]" % (p.lint_name(), r), report)

            for idx in range(filter_min_line, len(lines)):

                if filter_max_findings is not None:
                    if num_findings == filter_max_findings:
                        break

                if filter_max_line is not None:
                    if (idx+1) == filter_max_line:
                        break

                v, r = p.lint_cycle(plugins_params, fn, shared_state, (idx+1), lines[idx])
                if not v:
                    return False, ("Plugin [%s] failed (cycle): [%s]" % (p.lint_name(), r), report)

                v, r = helper_process_result(r, report, autocorrect, lines_copy)
                if not v:
                    return False, ("Plugin [%s] failed (cycle-result): [%s]" % (p.lint_name(), r), report)
                r_left, r_right = r
                num_findings += r_left
                num_patches_applied += r_right

            v, r = p.lint_post(plugins_params, fn, shared_state)
            if not v:
                return False, ("Plugin [%s] failed (post): [%s]" % (p.lint_name(), r), report)

            v, r = helper_process_result(r, report, autocorrect, lines_copy)
            if not v:
                return False, ("Plugin [%s] failed (post-result): [%s]" % (p.lint_name(), r), report)
            r_left, r_right = r
            num_findings += r_left
            num_patches_applied += r_right

            extra_str = helper_make_extra_plugin_end_str(num_findings, num_patches_applied)
            report.append((False, "Plugin: [%s] - end%s" % (p.lint_name(), extra_str)))

        if autocorrect and num_patches_applied > 0:
            os.unlink(f)
            create_and_write_file.create_file_contents(f, string_utils.line_list_to_string(lines_copy))
        report.append((False, "Processing [%s] - end" % f))

    return True, report

def print_report(report):

    any_findings = False
    for e in report:
        if e[0]:
            print("%s%s%s" % (terminal_colors.TTY_YELLOW, e[1], terminal_colors.get_standard_color()))
            any_findings = True
        else:
            print(e[1])
    return any_findings

def applet_helper(plugins, plugins_params, filters, autocorrect, skip_non_utf8, files):

    v, r = codelint(plugins, plugins_params, filters, autocorrect, skip_non_utf8, files)
    if not v:
        print("%s%s%s" % (terminal_colors.TTY_RED, r[0], terminal_colors.get_standard_color()))
        if len(r[1]) > 0:
            print("\n%sPartially generated report:%s\n" % (terminal_colors.TTY_RED_BOLD, terminal_colors.get_standard_color()))
            print_report(r[1])
        sys.exit(CODELINT_CMDLINE_RETURN_ERROR)
    print("%sComplete report%s:\n" % (terminal_colors.TTY_WHITE_BOLD, terminal_colors.get_standard_color()))
    if print_report(r):
        print("\n%sAll operations suceeded - with findings%s" % (terminal_colors.TTY_GREEN_BOLD, terminal_colors.get_standard_color()))
        sys.exit(CODELINT_CMDLINE_RETURN_PLUGIN_FINDING)
    else:
        print("\n%sAll operations suceeded - no findings%s" % (terminal_colors.TTY_GREEN, terminal_colors.get_standard_color()))

def files_from_folder(folder, extensions):

    v, r = fsquery.makecontentlist(folder, True, True, True, False, True, False, True, extensions)
    return v, r

def puaq(selfhelp):
    print("Usage: %s [--help] [--plugin (see below)] [--plugin-param name value] [--autocorrect (only one plugin allowed per run)] [--skip-non-utf8] [--files [targets] | --folder target [extensions]]" % path_utils.basename_filtered(__file__))
    print("\nPlugin list:")
    for p in plugin_table:
        print("* %s %s (%s)" % (p, plugin_table[p][1], plugin_table[p][0].lint_desc()))
    print("\nFilter list:")
    for f in filter_table:
        print("* %s %s (%s)" % (f, filter_table[f][0], filter_table[f][1]))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(CODELINT_CMDLINE_RETURN_ERROR)

if __name__ == "__main__":

    if "--help" in sys.argv[1:]:
        puaq(True)

    if len(sys.argv) < 3:
        puaq(False)

    plugins = []
    plugins_params = {}
    filters = {}
    autocorrect = False
    skip_non_utf8 = False
    files = None
    folder = None
    extensions = None

    plugin_next = False
    plugin_param_name = None
    plugin_param_name_next = False
    plugin_param_value_next = False
    filter_name = None
    filter_name_next = False
    filter_value_next = False
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
                print("Unregistered plugin: [%s]" % p)
                sys.exit(CODELINT_CMDLINE_RETURN_ERROR)
            plugins.append(p)
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

        if filter_value_next:
            filter_value_next = False
            if filter_name in filters:
                filters[filter_name].append(p)
            else:
                filters[filter_name] = [p]
            filter_name = None
            continue

        if filter_name_next:
            filter_name_next = False
            if not p in filter_table:
                print("Unregistered filter: [%s]" % p)
                sys.exit(CODELINT_CMDLINE_RETURN_ERROR)
            filter_value_next = True
            filter_name = p
            continue

        if p == "--plugin":
            plugin_next = True

        elif p == "--plugin-param":
            plugin_param_name_next = True

        elif p == "--autocorrect":
            autocorrect = True

        elif p == "--skip-non-utf8":
            skip_non_utf8 = True

        elif p == "--filter":
            filter_name_next = True

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

    if filter_name_next:
        print("Missing filter name")
        sys.exit(CODELINT_CMDLINE_RETURN_ERROR)

    if filter_value_next:
        print("Missing filter value (expected for [%s])" % filter_name)
        sys.exit(CODELINT_CMDLINE_RETURN_ERROR)

    if files_next:
        files = sys.argv[idx+1:]
    elif folder_next:

        if len(sys.argv) > (idx+1):
            extensions = sys.argv[idx+1:]

        v, r = files_from_folder(folder, extensions)
        if not v:
            print(r)
            sys.exit(CODELINT_CMDLINE_RETURN_ERROR)
        files = r

    else:
        print("Neither --files nor --folder chosen")
        sys.exit(CODELINT_CMDLINE_RETURN_ERROR)

    applet_helper(plugins, plugins_params, filters, autocorrect, skip_non_utf8, files)
