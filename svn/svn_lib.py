#!/usr/bin/env python3

import sys
import os

import svn_wrapper
import path_utils

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

def get_list_unversioned(repo):

    v, r = svn_wrapper.status(repo)
    if not v:
        return False, r
    unversioned_files = [x for x in r.split(os.linesep) if x != ""]
    return True, unversioned_files

def get_previous_list(repo, previous_number):

    v, r = svn_wrapper.log(repo, str(previous_number))
    if not v:
        return False, r
    log_out = r

    sep_line = detect_separator(log_out)
    log_entries_pre = log_out.split(sep_line)
    log_entries = []
    for le in log_entries_pre:
        if le != "":
            log_entries.append(le)

    prev_list = rev_entries_filter(log_entries)
    return True, prev_list

def get_head_revision(repo):

    v, r = svn_wrapper.info(repo)
    if not v:
        return False, r
    head_rev = revision_filter_function(r)
    return True, head_rev

def is_svn_repo(repo):

    if not os.path.exists(repo):
        return False, "svn_lib.is_svn_repo failed: %s does not exist." % repo

    # should ideally use "svnlook info the_path" but that wouldn't work with some repositories
    the_svn_obj = path_utils.concat_path(repo, ".svn")
    if os.path.exists(the_svn_obj) and os.path.isdir(the_svn_obj):
        return True, "svn"
    return True, False
