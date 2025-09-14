#!/usr/bin/env python

import sys
import os
import time

import mvtools_envvars
import path_utils
import string_utils
import svn_wrapper

import log_helper
import get_platform
import convcygpath
import maketimestamp
import output_backup_helper

def _detect_conflicts(output):
    if output is None:
        return False
    n = output.find("Summary of conflicts:")
    if n != -1:
        return True
    return False

def fix_cygwin_path(path):

    if path is None:
        return None

    if not isinstance(path, str):
        return None

    if path == "":
        return None

    pf = get_platform.getplat()
    if pf == get_platform.PLAT_CYGWIN:
        return convcygpath.convert_cygwin_path_to_win_path(path)
    return path

def sanitize_windows_path(path):

    if path is None:
        return None

    if not isinstance(path, str):
        return None

    if path == "":
        return None

    local_path = path
    pf = get_platform.getplat()
    if pf in [get_platform.PLAT_CYGWIN, get_platform.PLAT_WINDOWS]:
        local_path = path_utils.compat_windows_path(local_path)
    return local_path

def is_non_generic(char_input, list_select):
    for c in list_select:
        if c == char_input:
            return False
    return True

def is_nonnumber(thechar):
    return is_non_generic(thechar, ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])

def is_nonspaceortabs(thechar):
    return is_non_generic(thechar, [" ", "\t"])

def has_string_in_list(the_list, the_str):
    for li in the_list:
        if the_str in li:
            return True
    return False

def extract_file_from_status_line(the_line):

    if len(the_line) < 9:
        return None
    if the_line[0:8] == "        ":
        return None
    return the_line[8:]

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

    return None

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

def revision_filter_function(the_output):

    find_string = "Last Changed Rev: "
    n = the_output.find(find_string)
    revision_left = the_output[n + len(find_string):]
    revision = ""
    for i in range(len(revision_left)):
        if is_nonnumber(revision_left[i]):
            revision = revision_left[0:i]
            break
    if len(revision) > 1:
        if revision[0] != "r":
            revision = "r%s" % revision
    return revision

def remote_link_filter_function(the_output):

    find_string = "URL: "

    the_output_filtered = string_utils.convert_dos_to_unix(the_output)
    the_output_filtered_split = the_output_filtered.split("\n")

    for l in the_output_filtered_split:
        if len(l) < len(find_string)+1:
            continue
        n = l.find(find_string)
        if n != 0:
            continue
        return l[len(find_string):]

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

    return None

def get_list_externals(local_repo):

    if local_repo is None:
        return False, "repo is unspecified"
    local_repo_final = os.path.abspath(local_repo)
    if not os.path.exists(local_repo_final):
        return False, "Repo path [%s] does not exist." % local_repo_final

    # sample of actual output from svn status, as of m2021 (on Linux): "Performing status on external item at 'ext/Subversion':"
    EXT_ST_MSG = "Performing status on external item at"

    v, r = svn_wrapper.status(local_repo_final)
    if not v:
        return False, r
    output = r
    lines = output.strip().split(os.linesep)

    list_externals = []

    for l in lines:
        stripped_line = l.strip()
        if len(stripped_line) == 0:
            continue
        slf = stripped_line.find(EXT_ST_MSG)
        if slf != -1:
            cropped_line = stripped_line[len(EXT_ST_MSG)+2:] # crop left
            cropped_line = cropped_line[:len(cropped_line)-2] # crop right
            final_ext_path = path_utils.concat_path(local_repo_final, cropped_line)
            list_externals.append(sanitize_windows_path(final_ext_path))

    return True, list_externals

def get_list_unversioned(local_repo):

    if local_repo is None:
        return False, "repo is unspecified"
    local_repo_final = os.path.abspath(local_repo)
    if not os.path.exists(local_repo_final):
        return False, "Repo path [%s] does not exist." % local_repo_final

    v, r = svn_wrapper.status(local_repo_final)
    if not v:
        return False, r
    unversioned_files = [status_filter_function_unversioned(x) for x in r.split(os.linesep) if x != ""]
    unversioned_files = [path_utils.concat_path(local_repo_final, sanitize_windows_path(x)) for x in unversioned_files if x is not None]
    return True, unversioned_files

def get_previous_list(local_repo, previous_number=None):

    if local_repo is None:
        return False, "repo is unspecified"
    local_repo_final = os.path.abspath(local_repo)
    if not os.path.exists(local_repo_final):
        return False, "Repo path [%s] does not exist." % local_repo_final

    if previous_number is not None:
        previous_number = str(previous_number)
    v, r = svn_wrapper.log(local_repo_final, previous_number)
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

def repo_has_any_not_of_states(local_repo, states):

    list_unexpected = []

    if states is None:
        return False, "states is unspecified"

    if not isinstance(states, list):
        return False, "states is not a list"

    if local_repo is None:
        return False, "repo is unspecified"
    local_repo_final = os.path.abspath(local_repo)
    if not os.path.exists(local_repo_final):
        return False, "Repo path [%s] does not exist." % local_repo_final

    v, r = svn_wrapper.status(local_repo_final)
    if not v:
        return False, r
    if len(states) == 0:
        return True, []

    for line in r.split(os.linesep):

        if len(line.strip()) == 0:
            break

        if "local file edit, incoming replace with dir upon update" in line:
            continue
        if "Summary of conflicts" in line:
            continue
        if "Text conflicts" in line:
            continue
        if "Tree conflicts" in line:
            continue
        if "> moved to" in line:
            continue
        if "> moved from" in line:
            continue

        item_status = line[0]

        if item_status not in states:
            list_unexpected.append(item_status)

    return True, list_unexpected

def get_head_files(local_repo):

    total_entries = []

    funcs = [get_head_modified_files, get_head_missing_files, get_head_added_files, get_head_deleted_files, get_head_replaced_files, get_head_conflicted_files]

    for f in funcs:
        v, r = f(local_repo)
        if not v:
            return False, r
        total_entries += r

    return True, total_entries

def get_head_modified_files(local_repo):
    return get_head_files_delegate(local_repo, "M")

def get_head_missing_files(local_repo):
    return get_head_files_delegate(local_repo, "!")

def get_head_added_files(local_repo):
    return get_head_files_delegate(local_repo, "A")

def get_head_deleted_files(local_repo):
    return get_head_files_delegate(local_repo, "D")

def get_head_replaced_files(local_repo):
    return get_head_files_delegate(local_repo, "R")

def get_head_conflicted_files(local_repo):
    return get_head_files_delegate(local_repo, "C")

def get_head_type_changed_files(local_repo):
    return get_head_files_delegate(local_repo, "~")

def get_head_files_delegate(local_repo, status_detect):

    if local_repo is None:
        return False, "repo is unspecified"
    local_repo_final = os.path.abspath(local_repo)
    if not os.path.exists(local_repo_final):
        return False, "Repo path [%s] does not exist." % local_repo_final

    v, r = svn_wrapper.status(local_repo_final)
    if not v:
        return False, r

    mod_list = []

    for line in r.split(os.linesep):

        if len(line.strip()) == 0:
            break
        item_status = line[0]

        if item_status == status_detect:
            mod_file = extract_file_from_status_line(line)
            if mod_file is None:
                return False, "Unable to detect file from status line: [%s]" % line
            mod_list.append(path_utils.concat_path(local_repo_final, sanitize_windows_path(mod_file)))

    return True, mod_list

def get_head_revision(local_repo):
    return svn_info_delegate(local_repo, revision_filter_function)

def get_remote_link(local_repo):
    return svn_info_delegate(local_repo, remote_link_filter_function)

def svn_info_delegate(local_repo, output_filter_function):

    if local_repo is None:
        return False, "repo is unspecified"
    local_repo_final = os.path.abspath(local_repo)
    if not os.path.exists(local_repo_final):
        return False, "Repo path [%s] does not exist." % local_repo_final

    v, r = svn_wrapper.info(local_repo_final)
    if not v:
        return False, r
    filtered_output = output_filter_function(r)
    return True, filtered_output

def is_svn_repo(local_repo):

    if local_repo is None:
        return False, "repo is unspecified"
    local_repo_final = os.path.abspath(local_repo)
    if not os.path.exists(local_repo_final):
        return False, "Repo path [%s] does not exist." % local_repo_final

    # should ideally use "svnlook info the_path" but that wouldn't work with some repositories
    the_svn_obj = path_utils.concat_path(local_repo_final, ".svn")
    if os.path.exists(the_svn_obj) and os.path.isdir(the_svn_obj):
        return True, "svn"
    return True, False

def is_head_clear(local_repo, include_externals, ignore_unversioned):

    if local_repo is None:
        return False, "repo is unspecified"
    local_repo_final = os.path.abspath(local_repo)
    if not os.path.exists(local_repo_final):
        return False, "Repo path [%s] does not exist." % local_repo_final

    all_repos = [local_repo_final]

    if include_externals:
        v, r = get_list_externals(local_repo_final)
        if not v:
            return False, r
        all_repos += r

    for cr in all_repos:
        v, r = is_head_clear_delegate(cr, ignore_unversioned)
        if not v:
            return False, r
        if not r:
            return True, False

    return True, True

def is_head_clear_delegate(local_repo, ignore_unversioned):

    if local_repo is None:
        return False, "repo is unspecified"
    local_repo_final = os.path.abspath(local_repo)
    if not os.path.exists(local_repo_final):
        return False, "Repo path [%s] does not exist." % local_repo_final

    v, r = svn_wrapper.status(local_repo_final)
    if not v:
        return False, r
    st_items = r.split(os.linesep)

    clear_st = ["X", "I"]
    if ignore_unversioned:
        clear_st.append("?")
    for i in st_items:
        if i == "":
            break
        st_current_item = i[0]
        if not st_current_item in clear_st:
            return True, False

    return True, True

def revert(local_repo, repo_items):

    if local_repo is None:
        return False, "repo is unspecified"
    local_repo_final = os.path.abspath(local_repo)
    if not os.path.exists(local_repo_final):
        return False, "Repo path [%s] does not exist." % local_repo_final

    if not isinstance(repo_items, list):
        return False, "repo_items must be a list"
    if len(repo_items) == 0:
        return False, "repo_items can't be empty"

    repo_items_final = []
    for ri in repo_items:
        repo_items_final.append(fix_cygwin_path(ri))

    return svn_wrapper.revert(local_repo_final, repo_items_final)

def diff(local_repo, file_list=None, rev=None):

    if local_repo is None:
        return False, "repo is unspecified"
    local_repo_final = os.path.abspath(local_repo)
    if not os.path.exists(local_repo_final):
        return False, "Repo path [%s] does not exist." % local_repo_final

    file_list_final = None
    if file_list is not None:
        file_list_final = []

        if not isinstance(file_list, list):
            return False, "file_list must be a list"
        if len(file_list) == 0:
            return False, "file_list can't be empty"

        for fi in file_list:

            # cut out the full preceding path of the files in relation to the base source repo
            # this is necessary to make the patches portable. as of nov/21, svn version 1.13 does
            # not offer a switch to do this on its own

            v, r = path_utils.based_path_find_outstanding_path(local_repo, fi)
            if not v:
                return False, "Unable to find outstanding path between [%s] and [%s]" % (local_repo, fi)
            fi_local = r

            file_list_final.append(fi_local)

    return svn_wrapper.diff(local_repo_final, file_list_final, rev)

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

    try:

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

    except:
        pass
    return False

def _update_autorepair_check_return(output_message):
    return _check_valid_codes(output_message, ["E205011", "W000104"])

def _update_and_cleanup(feedback_object, local_repo, autobackups):

    if local_repo is None:
        return False, "repo is unspecified"
    local_repo_final = os.path.abspath(local_repo)
    if not os.path.exists(local_repo_final):
        return False, "Repo path [%s] does not exist." % local_repo_final

    warnings = None

    # cleanup
    v, r = svn_wrapper.cleanup(local_repo_final)
    if not v:
        return False, r
    proc_result = r[0]
    proc_stdout = r[1]
    proc_stderr = r[2]

    output_list = [("svn_lib_cleanup_stdout", proc_stdout, "Svn's cleanup stdout"), ("svn_lib_cleanup_stderr", proc_stderr, "Svn's cleanup stderr")]
    warnings = log_helper.add_to_warnings(warnings, output_backup_helper.dump_outputs_autobackup(((not autobackups) or proc_result), feedback_object, output_list))

    if not proc_result:
        return False, proc_stderr

    # update
    v, r = svn_wrapper.update_postpone(local_repo_final)
    if not v:
        return False, r
    proc_result = r[0]
    proc_stdout = r[1]
    proc_stderr = r[2]
    if _detect_conflicts(proc_stdout):
        feedback_object("   WARNING! Conflicts detected!   ")
    if proc_result:
        return True, None

    output_list = [("svn_lib_update_stdout", proc_stdout, "Svn's update stdout"), ("svn_lib_update_stderr", proc_stderr, "Svn's update stderr")]
    warnings = log_helper.add_to_warnings(warnings, output_backup_helper.dump_outputs_autobackup(((not autobackups) or proc_result), feedback_object, output_list))

    # check update's result
    if not _update_autorepair_check_return(proc_stdout):
        return False, "unable to parse svn's output for reattempts" # failed, irrecoverably. give up.
    warnings = log_helper.add_to_warnings(warnings, "update_autorepair warning: update operation failed but was accepted for repairing (at %s)." % local_repo_final)

    return True, (warnings, proc_stdout)

def update_autorepair(feedback_object, local_repo, do_recursion, autobackups):

    if local_repo is None:
        return False, "repo is unspecified"
    local_repo_final = os.path.abspath(local_repo)
    if not os.path.exists(local_repo_final):
        return False, "Repo path [%s] does not exist." % local_repo_final

    warnings = None
    iterations = 0
    MAX_ITERATIONS = 6

    while True:

        # loop sentinel
        iterations += 1
        if iterations > MAX_ITERATIONS:
            return False, "update_autorepair: max iterations [%s] exceeded (at %s)" % (MAX_ITERATIONS, local_repo_final)

        v, r = _update_and_cleanup(feedback_object, local_repo_final, autobackups)
        if not v:
            return False, r # failed, irrecoverably. give up.
        if r is None:
            break # both cleanup and update worked. we're done.

        # failed but its possible to attempt to autorepair it.
        warnings = log_helper.add_to_warnings(warnings, r[0])
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
                externals_full_path = path_utils.concat_path(local_repo_final, external_path)
                v, r = update_autorepair(externals_full_path, False)
                if not v:
                    return False, r
                warnings = log_helper.add_to_warnings(warnings, r)

    return True, warnings

def _checkout_autorepair_check_return(output_message):
    return _check_valid_codes(output_message, ["E205011", "W000104"])

def checkout_with_update(feedback_object, remote_link, local_repo, autobackups):

    if local_repo is None:
        return False, "repo is unspecified"
    local_repo_final = os.path.abspath(local_repo)
    if not os.path.exists(path_utils.dirname_filtered(local_repo_final)):
        return False, "Path (dirname) [%s] does not exist." % path_utils.dirname_filtered(local_repo_final)

    warnings = None

    v, r = svn_wrapper.checkout(remote_link, local_repo_final)
    if not v:
        return False, r
    proc_result = r[0]
    proc_stdout = r[1]
    proc_stderr = r[2]

    output_list = [("svn_lib_checkout_stdout", proc_stdout, "Svn's checkout stdout"), ("svn_lib_checkout_stderr", proc_stderr, "Svn's checkout stderr")]
    warnings = log_helper.add_to_warnings(warnings, output_backup_helper.dump_outputs_autobackup(((not autobackups) or proc_result), feedback_object, output_list))

    if not proc_result:
        if not _checkout_autorepair_check_return(proc_stdout):
            return False, proc_stderr
        warnings = log_helper.add_to_warnings(warnings, "checkout_autorepair warning: checkout operation failed but was accepted for repairing (at %s)." % local_repo_final)

    v, r = update_autorepair(feedback_object, local_repo_final, True, autobackups)
    if not v:
        return False, r
    warnings = log_helper.add_to_warnings(warnings, r)

    return True, warnings

def checkout_autoretry(feedback_object, remote_link, local_repo, autobackups):

    if local_repo is None:
        return False, "repo is unspecified"
    local_repo_final = os.path.abspath(local_repo)
    if not os.path.exists(path_utils.dirname_filtered(local_repo_final)):
        return False, "Path (dirname) [%s] does not exist." % path_utils.dirname_filtered(local_repo_final)

    warnings = None
    iterations = 0
    MAX_ITERATIONS = 6

    while True:

        # loop sentinel
        iterations += 1
        if iterations > MAX_ITERATIONS:
            return False, "repeated_checkout: max iterations [%s] exceeded (at %s)" % (MAX_ITERATIONS, local_repo_final)

        v, r = checkout_with_update(feedback_object, remote_link, local_repo_final, autobackups)
        if v:
            # this iteration worked. its done
            warnings = log_helper.add_to_warnings(warnings, r)
            return True, warnings

        # failed iteration. reset and start over
        warnings = log_helper.add_to_warnings(warnings, "Iteration [%d] failed and was sleep-retried. Reason: [%s]" % (iterations, r))
        path_utils.deletefolder_ignoreerrors(local_repo_final)
        SLEEP_TIME = 15 # minutes
        feedback_object("Iteration number [%d] has failed. Will sleep for [%d] minutes before retrying." % (iterations, SLEEP_TIME))
        time.sleep(SLEEP_TIME * 60)
        feedback_object("Iteration number [%d] will resume now (at %s)." % (iterations, maketimestamp.get_timestamp_now_compact()))

    return True, warnings

def _restore_subpath_check_return(output_message):
    return _check_valid_codes(output_message, ["E155000"])

def restore_subpath(repo, repo_subpath):

    if os.path.exists(repo_subpath):
        return False, "Unable to restore [%s]'s subpath [%s]: This subpath still exists." % (repo, repo_subpath)

    v, r = mvtools_envvars.mvtools_envvar_read_temp_path()
    if not v:
        return False, r
    temp_path_base = r

    # sanity checking
    if not os.path.exists(temp_path_base):
        return False, "Unable to restore [%s]'s subpath [%s]: Mvtools's temp path [%s] does not exist." % (repo, repo_subpath, temp_path_base)

    # get ts
    ts_now = maketimestamp.get_timestamp_now_compact()

    temp_path_leaf = "svn_lib_restore_path_%s_%s" % (path_utils.basename_filtered(repo), ts_now)
    temp_path_full = path_utils.concat_path(temp_path_base, temp_path_leaf)

    if os.path.exists(temp_path_full):
        return False, "Unable to restore [%s]'s subpath [%s]: The temporary final path [%s] already exists." % (repo, repo_subpath, temp_path_full)

    os.mkdir(temp_path_full)
    v, r = restore_subpath_delegate(repo, repo_subpath, temp_path_full)
    path_utils.deletefolder_ignoreerrors(temp_path_full)
    return v, r

def restore_subpath_delegate(repo, repo_subpath, temp_path_full):

    # get remote link
    v, r = get_remote_link(repo)
    if not v:
        return False, "Unable to restore [%s]'s subpath [%s]: Unable to fetch remote link: [%s]" % (repo, repo_subpath, r)
    remote_link = r

    # fetch head revision
    v, r = get_head_revision(repo)
    if not v:
        return False, "Unable to restore [%s]'s subpath [%s]: Unable to fetch head revision: [%s]" % (repo, repo_subpath, r)
    head_revision = r

    v, r = path_utils.based_path_find_outstanding_path(repo, repo_subpath)
    if not v:
        return False, "Unable to restore [%s]'s subpath [%s]: Unable to extract subpath from fullpath: [%s]" % (repo, repo_subpath, r)
    subpath_leftover = r

    iterations = 0
    MAX_ITERATIONS = 6

    while True:

        iterations += 1
        if iterations > MAX_ITERATIONS:
            return False, "Unable to restore [%s]'s subpath [%s]: SVN server failed too many (%s) times." % (repo, repo_subpath, MAX_ITERATIONS)

        # export to temp folder
        v, r = svn_wrapper.export(remote_link, subpath_leftover, fix_cygwin_path(temp_path_full), head_revision)
        if not v:
            return False, "Unable to restore [%s]'s subpath [%s]: Unable to export to local temp folder: [%s]" % (repo, repo_subpath, r)
        p_code = r[0]
        p_out = r[1]
        p_err = r[2]
        if p_code: # it worked. quit trying to export.
            break
        else: # the call to the svn process failed. let's investigate what happened.
            if _restore_subpath_check_return(p_err): # a known case - trying to export folders. treat as a success.
                break
            else: # unkown case - typically a network problem. just retry.
                SLEEP_TIME = 5 # minutes
                time.sleep(SLEEP_TIME * 60)
                continue

    local_exported_file = path_utils.concat_path(temp_path_full, path_utils.basename_filtered(subpath_leftover))
    if not os.path.exists(local_exported_file) and not path_utils.is_path_broken_symlink(local_exported_file):
        # most likely this was just a deleted folder. just recreate it.
        # this happens because svn export does not export one of the repository's folder to a locally pre-existing folder. (E155000 as of L21)
        if not path_utils.guaranteefolder(repo_subpath):
            return False, "Unable to restore [%s]'s subpath [%s]: Unable to guarantee folder [%s]." % (repo, repo_subpath, repo_subpath)
    else:
        # manually copy the exported file back onto the repo
        if not path_utils.guaranteefolder(path_utils.dirname_filtered(repo_subpath)):
            return False, "Unable to restore [%s]'s subpath [%s]: Unable to guarantee folder [%s]." % (repo, repo_subpath, path_utils.dirname_filtered(repo_subpath))
        v = path_utils.copy_to(local_exported_file, path_utils.dirname_filtered(repo_subpath))
        if not v:
            return False, "Unable to restore [%s]'s subpath [%s]: Unable to copy exported file [%s] back to the local repository." % (repo, repo_subpath, local_exported_file)

    return True, None

def kill_previous(target_repo, num_previous):

    if target_repo is None:
        return False, "repo is unspecified"
    target_repo_final = os.path.abspath(target_repo)
    if not os.path.exists(target_repo_final):
        return False, "Repo path [%s] does not exist." % target_repo_final

    v, r = get_previous_list(target_repo, num_previous+1)
    if not v:
        return False, "Unable to retrieve previous revision list, from repo [%s]: [%s]. Requested quantity: [%d]" % (target_repo, r, num_previous)
    prev_revs = r

    if len(prev_revs) < 2:
        return False, "Unable to rewind to previous revision, on repo [%s]. Not enough previous revisions found (minimum is 2)." % (target_repo)

    if num_previous >= len(prev_revs):
        return False, "Unable to rewind to previous revision, on repo [%s]. More or equal rewinds requested than there are previous revisions available ([%d] vs. [%d])." % (target_repo, num_previous, len(prev_revs))

    last_rev = prev_revs[len(prev_revs)-1]
    v, r = svn_wrapper.update_revision(target_repo, last_rev)
    if not v:
        return False, "Unable to rewind to previous revision, on repo [%s]: [%s]. Attempted revision: [%d]" % (target_repo, r, last_rev)

    return True, None

def patch_as_head(repo, patch_file, override_head_check):

    if repo is None:
        return False, "repo is unspecified"
    repo_final = os.path.abspath(repo)
    if patch_file is None:
        return False, "patch_file is unspecified"
    patch_file_final = fix_cygwin_path(patch_file)

    if not override_head_check:
        v, r = is_head_clear(repo_final, False, False)
        if not v:
            return False, r
        if not r:
            return False, "Cannot patch - head is not clear"

    v, r = svn_wrapper.patch(repo_final, patch_file_final)
    if not v:
        return False, r

    return True, None
