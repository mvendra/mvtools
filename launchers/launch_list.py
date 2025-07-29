#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run
import sanitize_terminal_line

def run_list(runnable_list, verbose=False, base_path=None, adapter=None):

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

        fullcmd = []
        if adapter is not None:
            fullcmd = [adapter, fullpath]
        else:
            fullcmd = [fullpath]

        if verbose:
            print("Now running: %s" % fullcmd)

        v, r = generic_run.run_cmd_simple(fullcmd)
        if not v:
            has_any_failed = True
            report.append( (False, "%s failed: %s" % (s, r) ) )
        else:
            print(r, end="")
            report.append( (True, s) )

    return (not has_any_failed, report)

def print_report(v, r):
    if not v:
        for i in r:
            if not i[0]:
                print("[%s] failed." % i[1])
        sys.exit(1)

    print("%s: All succeeded." % path_utils.basename_filtered(__file__))

def puaq(selfhelp):
    print("Usage: %s [--nocwd] [--adapter the_adapter] runnable_list" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq(False)

    runnable_list = sys.argv[1:]
    verbose = False
    the_cwd = os.getcwd()
    adapter = None

    # get optional params
    while True:
        if not len(runnable_list) > 0:
            break

        if runnable_list[0] == "--verbose":
            verbose = True
            runnable_list = runnable_list[1:]
        elif runnable_list[0] == "--nocwd":
            the_cwd = None
            runnable_list = runnable_list[1:]
        elif runnable_list[0] == "--adapter":
            if not len(runnable_list) > 1: # no actual adapter specified
                print("--adapter switch has been specified, but no actual adapter specified.")
                sys.exit(1)
            adapter = runnable_list[1]
            runnable_list = runnable_list[2:]
        else:
            break

    if len(runnable_list) == 0:
        print("%s: Nothing to run." % path_utils.basename_filtered(__file__))
        sys.exit(0)

    # runs the list
    v, r = run_list(runnable_list, verbose, the_cwd, adapter)

    # print the report
    print_report(v, r)
