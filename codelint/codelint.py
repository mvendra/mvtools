#!/usr/bin/env python3

import sys
import os

import path_utils
import getcontents

# plugins
import lint_sample_echo

def puaq():
    print("Usage: %s [--autocorrect (only one linter/plugin allowed per run)] [--lint-sample-echo | --mvtodo-other-plugins] [file-list]" % path_utils.basename_filtered(__file__))
    sys.exit(1)

def codelint(autocorrect, plugins, filelist):

    # preconds
    if not isinstance(autocorrect, bool):
        return False, "autocorrect is not bool"
    if not isinstance(plugins, list):
        return False, "plugins is not a list"
    if not isinstance(filelist, list):
        return False, "filelist is not a list"

    if len(plugins) < 1:
        return False, "No plugins selected"

    if autocorrect and len(plugins) > 1:
        return False, "Only one plugin is allowed to be executed with autocorrect turned on"

    for f in filelist:
        if not os.path.exists(f):
            return False, "File [%s] does not exist" % f

    # mvtodo: need to setup a feedback mechanism, for both cycle and post, for either changes or just reporting (reporting == such-and-such is wrong, go fix it yourself manually)

    report = []

    for f in filelist:

        shared_state = {}

        fn = path_utils.basename_filtered(f)
        contents = getcontents.getcontents(f)
        lines = contents.split("\n")

        report.append("Processing [%s] - begin" % f)

        for p in plugins:

            report.append("Plugin: [%s] - begin" % p.lint_name())
            p.lint_pre(autocorrect, fn, shared_state, len(lines))

            idx = 0
            for l in lines:
                idx += 1

                p.lint_cycle(autocorrect, fn, shared_state, idx, l)

            p.lint_post(autocorrect, fn, shared_state)
            report.append("Plugin: [%s] - end" % p.lint_name())

        report.append("Processing [%s] - end" % f)

    return True, None

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    autocorrect = False
    plugins = []
    filelist = None

    idx = 0
    for p in sys.argv[1:]:
        idx += 1

        if p == "--autocorrect":
            autocorrect = True
        elif p == "--lint-sample-echo":
            plugins.append(lint_sample_echo)

    filelist = sys.argv[idx:]

    v, r = codelint(autocorrect, plugins, filelist)
    if not v:
        print(r)
        sys.exit(1)
