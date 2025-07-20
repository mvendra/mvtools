#!/usr/bin/env python3

import sys
import os

import path_utils
import getcontents
import terminal_colors

# plugins
import lint_sample_echo
import lint_c_integer_suffix

def helper_validate_cycle_return(msg, patches):

    if not isinstance(msg, str):
        return False, "invalid cycle return: msg is not a str"

    if not isinstance(patches, list):
        return False, "invalid cycle return: patches is not a list"

    for e in patches:

        if not isinstance(e, tuple):
            return False, "invalid cycle return: patches entry is not a tuple"

        if not isinstance(e[0], int):
            return False, "invalid cycle return: patches entry, first tuple entry is not an int"

        if not isinstance(e[1], str):
            return False, "invalid cycle return: patches entry, second tuple entry is not a str"

    return True, None

def codelint(plugins, plugins_params, autocorrect, filelist):

    report = []

    # preconds
    if not isinstance(autocorrect, bool):
        return False, ("autocorrect is not bool", report)

    if not isinstance(plugins, list):
        return False, ("plugins is not a list", report)

    if not isinstance(filelist, list):
        return False, ("filelist is not a list", report)

    if len(plugins) < 1:
        return False, ("No plugins selected", report)

    if autocorrect and len(plugins) > 1:
        return False, ("Only one plugin is allowed to be executed with autocorrect turned on", report)

    if len(filelist) < 1:
        return False, ("No target files selected", report)

    for f in filelist:
        if not os.path.exists(f):
            return False, ("File [%s] does not exist" % f, report)

    for f in filelist:

        shared_state = {}

        fn = path_utils.basename_filtered(f)
        contents = getcontents.getcontents(f)
        lines = contents.split("\n")

        report.append((False, "Processing [%s] - begin" % f))

        for p in plugins:

            report.append((False, "Plugin: [%s] - begin" % p.lint_name()))
            v, r = p.lint_pre(plugins_params, autocorrect, fn, shared_state, len(lines))
            if not v:
                return False, ("Plugin [%s] failed (pre): [%s]" % (p.lint_name(), r), report)

            idx = 0
            for l in lines:
                idx += 1

                v, r = p.lint_cycle(plugins_params, autocorrect, fn, shared_state, idx, l)
                if not v:
                    return False, ("Plugin [%s] failed (cycle): [%s]" % (p.lint_name(), r), report)
                if r is not None:
                    msg, patches = r
                    v, r = helper_validate_cycle_return(msg, patches)
                    if not v:
                        return False, (r, report)
                    report.append((True, msg))

                    # mvtodo: apply {patches} if autocorrect is on

            v, r = p.lint_post(plugins_params, autocorrect, fn, shared_state)
            if not v:
                return False, ("Plugin [%s] failed (post): [%s]" % (p.lint_name(), r), report)
            report.append((False, "Plugin: [%s] - end" % p.lint_name()))

        report.append((False, "Processing [%s] - end" % f))

    return True, report

def print_report(report):

    for e in report:
        if e[0]:
            print("%s%s%s" % (terminal_colors.TTY_YELLOW, e[1], terminal_colors.TTY_WHITE))
        else:
            print(e[1])

def puaq():
    print("Usage: %s [--plugin (see below)] [--plugin-param name value] [--autocorrect (only one plugin allowed per run)] [filelist] [--help]" % path_utils.basename_filtered(__file__))
    print("Plugin list:")
    print("* lint-sample-echo {lint-sample-echo-pattern-match -> pattern}")
    print("* lint-c-int-suf {}")
    sys.exit(1)

if __name__ == "__main__":

    if "--help" in sys.argv[1:]:
        puaq()

    if len(sys.argv) < 3:
        puaq()

    plugin_table = {}
    plugin_table["lint-sample-echo"] = lint_sample_echo
    plugin_table["lint-c-int-suf"] = lint_c_integer_suffix

    plugins = []
    plugins_params = {}
    autocorrect = False
    filelist = None

    plugin_next = False
    plugin_param_name = None
    plugin_param_name_next = False
    plugin_param_value_next = False

    idx = 0
    for p in sys.argv[1:]:
        idx += 1

        if plugin_next:
            plugin_next = False
            if not p in plugin_table:
                print("Plugin [%s] does not exist" % p)
                sys.exit(1)
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
        else:
            idx -= 1
            break

    if plugin_param_name_next:
        print("Missing plugin param name!")
        sys.exit(1)

    if plugin_param_value_next:
        print("Missing plugin param value (expected for [%s])!" % plugin_param_name)
        sys.exit(1)

    filelist = sys.argv[idx+1:]

    v, r = codelint(plugins, plugins_params, autocorrect, filelist)
    if not v:
        print("%s%s%s" % (terminal_colors.TTY_RED, r[0], terminal_colors.TTY_WHITE))
        if len(r[1]) > 0:
            print("\n%sPartially generated report:%s\n" % (terminal_colors.TTY_RED_BOLD, terminal_colors.TTY_WHITE))
            print_report(r[1])
        sys.exit(1)
    print("%sComplete report%s:\n" % (terminal_colors.TTY_WHITE_BOLD, terminal_colors.TTY_WHITE))
    print_report(r)
    print("\n%sAll operations suceeded%s" % (terminal_colors.TTY_GREEN, terminal_colors.TTY_WHITE))
