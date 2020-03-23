#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run
import sanitize_terminal_line

def run_list(runnable_list, base_path=None):

    # first, sanitizes the list, so as to be compatible with terminal inputs
    san_run_list = []
    for r in runnable_list:
        san_run_list.append(sanitize_terminal_line.sanitize_terminal_line(r))

    # then run the list
    report = []
    has_any_failed = False
    for s in san_run_list:

        fullpath = s
        if base_path is not None:
            fullpath = path_utils.concat_path(base_path, s)

        if os.path.isdir(fullpath):
            continue

        v, r = generic_run.run_cmd_l(fullpath)
        if not v:
            has_any_failed = True
            report.append( (False, s, r) )
        else:
            report.append( (True, s, "") )

    return (not has_any_failed, report)

def puaq():
    print("Usage: %s runnable_list" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    v, r = run_list(sys.argv[1:], os.getcwd())

    if not v:
        for i in r:
            if not i[0]:
                print("[%s] failed: [%s]" % (i[1], i[2]))
        sys.exit(1)

    print("%s: All succeeded." % os.path.basename(__file__))
