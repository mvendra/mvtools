#!/usr/bin/env python3

import sys
import os

import path_utils
import getcontents
import terminal_colors

# plugins
import lint_sample_echo

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

    for f in filelist:
        if not os.path.exists(f):
            return False, ("File [%s] does not exist" % f, report)

    # mvtodo: need to setup a feedback mechanism, for both cycle and post, for either changes or just reporting (reporting == such-and-such is wrong, go fix it yourself manually)

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
                    report.append((True, r[0]))

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
    print("Usage: %s [--lint-sample-echo | --mvtodo-other-plugins] [mvtodo: plugins-params] [--autocorrect (only one linter/plugin allowed per run)] [file-list]" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    plugins = []
    plugins_params = {}
    autocorrect = False
    filelist = None

    idx = 0
    for p in sys.argv[1:]:
        idx += 1

        if p == "--lint-sample-echo":
            plugins.append(lint_sample_echo)
        elif p == "--autocorrect":
            autocorrect = True

    filelist = sys.argv[idx:]

    v, r = codelint(plugins, plugins_params, autocorrect, filelist)
    if not v:
        print("%s%s%s" % (terminal_colors.TTY_RED, r[0], terminal_colors.TTY_WHITE))
        print("Partially generated report:")
        print_report(r[1])
        sys.exit(1)
    print("Complete report:")
    print_report(r)
    print("\n%sAll operations suceeded%s" % (terminal_colors.TTY_GREEN, terminal_colors.TTY_WHITE))
