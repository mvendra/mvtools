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

def has_string_in_list(the_list, the_str):
    for li in the_list:
        if the_str in li:
            return True
    return False

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

def _parse_externals_update_message(output_message):

    MATCH_PHRASE_BEGIN = "Fetching external item into '"
    MATCH_PHRASE_END = "External at revision "

    om_lines = [x for x in output_message.split(os.linesep) if len(x) > 0]
    if len(om_lines) < 1:
        return None
    om_lines = om_lines[1:] # get rid of the "Updating '.':"
    if len(om_lines) < 2:
        return None
    if not MATCH_PHRASE_BEGIN in om_lines[0]:
        return None

    messages = []
    current_external_path = None
    current_external_messages = []

    for l in om_lines:

        if MATCH_PHRASE_BEGIN in l:

            # new external
            if current_external_path is not None:
                messages.append( (current_external_path, current_external_messages.copy()) )
                current_external_messages.clear()
            current_external_path = l[len(MATCH_PHRASE_BEGIN):len(l)-2]

        elif MATCH_PHRASE_END in l:

            # last (current) external just ended
            current_external_messages.append(l)
            messages.append( (current_external_path, current_external_messages.copy()) )
            current_external_messages.clear()
            current_external_path = None

        else:

            # abnormal / warnings / error messages
            current_external_messages.append(l)

    messages.append( (current_external_path, current_external_messages) ) # append the last entry

    return messages

def _check_valid_codes(output_message, valid_codes):

    om_lines = [x for x in output_message.split(os.linesep) if len(x) > 0]
    if len(om_lines) < 1:
        return False
    last_line = om_lines[len(om_lines)-1]

    if last_line == ".":
        if len(om_lines) < 2:
            return False
        om_lines = om_lines[:len(om_lines)-1]
        last_line = om_lines[len(om_lines)-1]

    for vc in valid_codes:
        if vc in last_line:
            return True
    return False

def _update_autorepair_check_return(output_message):
    return _check_valid_codes(output_message, ["E205011", "W000104"])

def _update_and_cleanup(local_repo):

    # cleanup
    v, r = svn_wrapper.cleanup(local_repo)
    if not v:
        return False, r

    # update
    v, r = svn_wrapper.update(local_repo)
    if v:
        return True, None

    # check update's result
    if not _update_autorepair_check_return(r):
        return False, r # failed, irrecoverably. give up.

    return True, ("update_autorepair warning: update operation failed but was accepted for repairing (at %s)." % local_repo, r)

def update_autorepair(local_repo, do_recursion):

    warnings = None
    iterations = 0
    MAX_ITERATIONS = 6

    while True:

        # loop sentinel
        iterations += 1
        if iterations > MAX_ITERATIONS:
            return False, "update_autorepair: max iterations [%s] exceeded (at %s)" % (MAX_ITERATIONS, local_repo)

        v, r = _update_and_cleanup(local_repo)
        if not v:
            return False, r # failed, irrecoverably. give up.
        if r is None:
            break # both cleanup and update worked. we're done.

        # failed but its possible to attempt to autorepair it.
        warnings = _add_to_warnings(warnings, r[0])
        output_message = r[1]

        if not do_recursion:
            continue

        externals_result = _parse_externals_update_message(output_message)
        if externals_result is None:
            return False, "Unparseable output message (can't parse the status of externals): [%s]" % output_message

        # try to autorepair externals that failed
        for er in externals_result:

            external_path = er[0]
            external_messages = er[1]

            if has_string_in_list(external_messages, "W155004"):
                externals_full_path = path_utils.concat_path(local_repo, external_path)
                v, r = update_autorepair(externals_full_path, False)
                if not v:
                    return False, r
                if r is not None:
                    warnings = _add_to_warnings(warnings, r)

    return True, warnings

def _checkout_autorepair_check_return(output_message):
    return _check_valid_codes(output_message, ["E205011", "W000104"])

def checkout_autorepair(remote_link, local_repo):

    warnings = None

    v, r = svn_wrapper.checkout(remote_link, local_repo)
    if not v:
        if not _checkout_autorepair_check_return(r):
            return False, r
        else:
            warnings = _add_to_warnings(warnings, "checkout_autorepair warning: checkout operation failed but was accepted for repairing (at %s)." % local_repo)

    v, r = update_autorepair(local_repo, True)
    if r is not None:
        warnings = _add_to_warnings(warnings, r)
    return v, warnings
