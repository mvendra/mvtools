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

def _add_to_warnings(warnings, latest_msg):
    if warnings is None:
        return latest_msg
    return "%s%s%s" % (warnings, os.linesep, latest_msg)

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
    unversioned_files = [status_filter_function_unversioned(x) for x in r.split(os.linesep) if x != ""]
    unversioned_files = [x for x in unversioned_files if x is not None] # mvtodo: there has to be a better way to do this
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

def revert(local_repo, repo_item):
    return svn_wrapper.revert(local_repo, repo_item)

def _check_valid_codes(output_message, valid_codes):

    om_lines = [x for x in output_message.split(os.linesep) if len(x) > 0]
    if len(om_lines) < 1:
        return False
    last_line = om_lines[len(om_lines)-1]

    for vc in valid_codes:
        if vc in last_line:
            return True
    return False

def _update_autorepair_check_return(local_repo):
    return _check_valid_codes(output_message, ["E205011"]) # the error code {E155016 - repository is corrupt} is irrecoverable, for example

def update_autorepair(local_repo):

    warnings = None
    iterations = 0
    MAX_ITERATIONS = 21

    while True:

        iterations += 1
        if iterations > MAX_ITERATIONS:
            return False, "update_autorepair: max iterations [%s] exceeded" % MAX_ITERATIONS

        v, r = svn_wrapper.cleanup(local_repo)
        if not v:
            return False, r

        v, r = svn_wrapper.update(local_repo)
        if v:
            break # both cleanup and update worked. we're done.
        output_message = r

        if not _update_autorepair_check_return(output_message):
            # failed, irrecoverably. give up.
            return False, r
        else:
            warnings = _add_to_warnings(warnings, "update_autorepair warning: update operation failed but was accepted for repairing.")
            """
            # mvtodo: it might be enough to just let it spin for a while. if not, then it would be necessary to parse the output of update
            like so:

            om_lines = [x for x in output_message.split(os.linesep) if len(x) > 0]
            if len(om_lines) < 1:
                return False, "Unparseable output message: [%s]" % output_message

            ... and then:

            # mvtodo: group together externals
            # mvtodo: find which externals failed, then cleanup+update those, one by one (issue warnings, mind the counters)
            # mvtodo: cleanup+update base one more time ( just continue into the next loop cycle - this would make the last MAX_ITERATIONS unsupported, but thats tolerable
            """

    return True, warnings

def _checkout_autorepair_check_return(output_message):
    return _check_valid_codes(output_message, ["E205011"])

def checkout_autorepair(remote_link, local_repo):

    warnings = None

    v, r = svn_wrapper.checkout(remote_link, local_repo)
    if not v:
        if not _checkout_autorepair_check_return(r):
            return False, r
        else:
            warnings = "checkout_autorepair warning: checkout operation failed but was accepted for repairing."

    v, r = update_autorepair(local_repo)
    if r is not None:
        warnings = "%s%s" % (os.linesep, warnings)
    return v, warnings
