#!/usr/bin/env python3

import sys
import os

import path_utils
import git_visitor_base
import git_lib
import git_wrapper
import terminal_colors

internal_options = {}

def print_success(msg):
    print("%s%s%s" % (terminal_colors.TTY_GREEN, msg, terminal_colors.get_standard_color()))

def print_warning(msg):
    print("%s%s%s" % (terminal_colors.TTY_YELLOW, msg, terminal_colors.get_standard_color()))

def print_error(msg):
    print("%s%s%s" % (terminal_colors.TTY_RED, msg, terminal_colors.get_standard_color()))

def git_config_remotes_internal(repos, options):

    for rp in repos:

        v, r = git_lib.get_remotes(rp)
        if not v:
            print_error(r)
            return False
        remotes = r

        if not internal_options["source_remote"] in remotes:
            print_error("Repo [%s] does not have a [%s] remote! Aborting." % (rp, internal_options["target_remote"]))
            return False

        if internal_options["target_remote"] in remotes:
            print_warning("Repo [%s] already has a [%s] remote! Skipping." % (rp, internal_options["target_remote"]))
            continue

        src_paths = remotes[internal_options["source_remote"]]

        # sanity-check: source's fetch and push should be the same
        if len(src_paths) < 2:
            print_error("Repo [%s] does not have two (fetch/push) remote paths! Aborting." % rp)
            return False

        if not "fetch" in src_paths:
            print_error("Repo [%s] does not have a fetch remote path" % rp)
            return False

        if not "push" in src_paths:
            print_error("Repo [%s] does not have a push remote path" % rp)
            return False

        if src_paths["fetch"] != src_paths["push"]:
            print_error("Repo [%s]'s fetch and push remotes are different - can't decide which one to use. Aborting." % rp)
            return False

        new_tg_path = "%s:%s" % (internal_options["target_remote_address"], src_paths["fetch"])

        v, r = git_wrapper.remote_add(rp, internal_options["target_remote"], new_tg_path)
        if not v:
            print_error("Repo [%s]: %s" % (rp, r))
            return False

def git_config_remotes():

    r = git_visitor_base.do_visit(None, None, git_config_remotes_internal)
    if False in r:
        return False
    return True

def puaq():
    print("Usage: %s source_remote target_remote target_remote_address" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 4:
        puaq()

    internal_options["source_remote"] = sys.argv[1]
    internal_options["target_remote"] = sys.argv[2]
    internal_options["target_remote_address"] = sys.argv[3]

    if not git_config_remotes():
        print_error("Operation failed.")
        sys.exit(1)
    print_success("Operation successful.")
