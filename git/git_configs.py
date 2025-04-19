#!/usr/bin/env python3

import sys
import git_lib

def call_and_assemble_report(report, cfg_key, cfg_val):
    v, r = git_lib.config(cfg_key, cfg_val, True)
    if not v:
        report.append(r)
    return report

def set_git_configs(name, email):

    report = call_and_assemble_report([], "user.name", name)
    report = call_and_assemble_report(report, "user.email", email)

    report = call_and_assemble_report(report, "diff.tool", "meld")
    report = call_and_assemble_report(report, "diff.external", "meldiff.py")
    report = call_and_assemble_report(report, "push.default", "simple")
    report = call_and_assemble_report(report, "init.defaultBranch", "master")
    report = call_and_assemble_report(report, "protocol.file.allow", "always")

    if len(report) > 0:
        print("Failures:")
        for ri in report:
            print(ri)
        sys.exit(1)
    else:
        print("All OK")

if __name__ == "__main__":

    name = input("Input your name.\n")
    email = input("Input your email.\n")
    set_git_configs(name, email)
