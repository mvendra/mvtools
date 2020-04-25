#!/usr/bin/env python3

import sys
import os

import generic_run

###########
# helpers #
###########

def is_non_generic(char_input, list_select):
    for c in list_select:
        if c == char_input:
            return False
    return True

def is_nonnumber(thechar):
    return is_non_generic(thechar, ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])

def is_nonspaceortabs(thechar):
    return is_non_generic(thechar, [" ", "\t"])

def status_filter_function_unversioned(the_line):
    if the_line is None:
        return None
    if len(the_line) == 0:
        return None
    if the_line[0] != "?":
        return None
    the_line = the_line[1:]

    for i in range(len(the_line)):
        if is_nonspaceortabs(the_line[i]):
            return the_line[i:]

def rev_single_entry_filter(log_entry):

    if log_entry is None:
        return None
    if len(log_entry) == 0:
        return None

    na = log_entry.find("r")
    if na == -1:
        return None
    nb = log_entry.find(" ", na)
    the_rev = log_entry[na:nb]
    return the_rev

def rev_entries_filter(log_entries_list):

    rev_list = []

    for le in log_entries_list:
        rle = rev_single_entry_filter(le)
        if rle is not None:
            rev_list.append(rle)

    return rev_list

def generic_parse(str_line, separator):
    if str_line is None:
        return None
    n = str_line.find(separator)
    if n == -1:
        return None
    return str_line[:n]

def revision_filter_function(the_output):

    find_string = "Revision: "
    n = the_output.find(find_string)
    revision_left = the_output[n + len(find_string):]
    revision = ""
    for i in range(len(revision_left)):
        if is_nonnumber(revision_left[i]):
            revision = revision_left[0:i]
            break
    return revision

def detect_separator(the_string):

    if the_string is None:
        return None
    if len(the_string) == 0:
        return None

    rep_char = the_string[0]
    rep_line = ""
    for i in range(len(the_string)):
        if is_non_generic(the_string[i], [rep_char]):
            rep_line = the_string[0:i]
            return rep_line

###############
# svn applets #
###############

def status(repo):

    if not os.path.exists(repo):
        return False, "%s does not exist." % repo

    v, r = generic_run.run_cmd_simple(["svn", "status"], use_cwd=repo)
    if not v:
        return False, "Failed calling svn-status command: %s." % r

    return v, r

def info(repo):

    if not os.path.exists(repo):
        return False, "%s does not exist." % repo

    v, r = generic_run.run_cmd_simple(["svn", "info"], use_cwd=repo)
    if not v:
        return False, "Failed calling svn-info command: %s." % r

    return v, r

def log(repo, limit=None):

    if not os.path.exists(repo):
        return False, "%s does not exist." % repo

    cmd = ["svn", "log"]
    if limit is not None:
        cmd.append("--limit")
        cmd.append(limit)

    v, r = generic_run.run_cmd_simple(cmd, use_cwd=repo)
    if not v:
        return False, "Failed calling svn-log command: %s." % r

    return v, r

def diff(repo, rev=None):

    if not os.path.exists(repo):
        return False, "%s does not exist." % repo

    cmd = ["svn", "diff", "--internal-diff"]
    if rev is not None:
        cmd.append("-c")
        cmd.append(rev)

    v, r = generic_run.run_cmd_simple(cmd, use_cwd=repo)
    if not v:
        return False, "Failed calling svn-diff command: %s." % r

    return v, r

def puaq():
    print("Usage: %s repo [--info | --status | --log | --diff]" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    repo = sys.argv[1]
    options = sys.argv[2:]

    print(options)
