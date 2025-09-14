#!/usr/bin/env python

import sys
import os

import path_utils
import maketimestamp
import mvtools_envvars
import mvtools_exception
import log_helper
import toolbus

OUTPUT_BACKUP_HELPER_TOOLBUS_DATABASE = "mvtools_output_backup_helper"
OUTPUT_BACKUP_HELPER_TOOLBUS_CONTEXT = "output_backup_helper"
OUTPUT_BACKUP_HELPER_TOOLBUS_INDEX = "index"
OUTPUT_BACKUP_HELPER_MAX_INDEX = 999

def _ensure_toolbus_db():

    v, r = toolbus.get_all_fields(OUTPUT_BACKUP_HELPER_TOOLBUS_DATABASE, OUTPUT_BACKUP_HELPER_TOOLBUS_CONTEXT)
    if v and r is not None:
        return True, None

    first_error = None
    v, r = toolbus.bootstrap_custom_toolbus_db(OUTPUT_BACKUP_HELPER_TOOLBUS_DATABASE)
    if not v:
        first_error = r # save it - this might be recoverable (if the db file is simply empty)

    v, r = toolbus.set_field(OUTPUT_BACKUP_HELPER_TOOLBUS_DATABASE, OUTPUT_BACKUP_HELPER_TOOLBUS_CONTEXT, OUTPUT_BACKUP_HELPER_TOOLBUS_INDEX, "0", [])
    if not v:
        errmsg = ""
        if first_error is None:
            errmsg = r
        else:
            errmsg = "First error: [%s]. Second error: [%s]" % (first_error, r)
        return False, errmsg

    return True, None

def dump_output(feedback_object, output_filename, output_contents, log_message):

    if output_filename is None:
        return

    if os.path.exists(output_filename):
        raise mvtools_exception.mvtools_exception("Output filename [%s] already exists." % output_filename)

    with open(output_filename, "w") as f:
        f.write(output_contents)
    feedback_object(log_message)

def dump_single_autobackup(feedback_object, base_path, output_fn_prefix, output_contents, output_log):

    v, r = _ensure_toolbus_db()
    if not v:
        return "toolbus error: [%s]" % r

    # get ts
    ts_now = maketimestamp.get_timestamp_now_compact()

    # get backup file index (this is used to avoid collisions - very common for quick operations, where the timestamp alone isn't enough
    v, r = toolbus.get_field(OUTPUT_BACKUP_HELPER_TOOLBUS_DATABASE, OUTPUT_BACKUP_HELPER_TOOLBUS_CONTEXT, OUTPUT_BACKUP_HELPER_TOOLBUS_INDEX)
    if not v:
        return "toolbus error: [%s]" % r
    backup_file_index = int(r[1])

    if backup_file_index > OUTPUT_BACKUP_HELPER_MAX_INDEX:
        backup_file_index = 0

    v, r = toolbus.set_field(OUTPUT_BACKUP_HELPER_TOOLBUS_DATABASE, OUTPUT_BACKUP_HELPER_TOOLBUS_CONTEXT, OUTPUT_BACKUP_HELPER_TOOLBUS_INDEX, str(backup_file_index+1), [])
    if not v:
        return "toolbus error: [%s]" % r

    output_filename = path_utils.concat_path(base_path, "%s_autobackup_%d_%s.txt" % (output_fn_prefix, backup_file_index, ts_now))
    if os.path.exists(output_filename):
        return "autobackup file [%s] already exists" % output_filename

    with open(output_filename, "w") as f:
        f.write(output_contents)
    feedback_object("%s has been saved to [%s]" % (output_log, output_filename))

    return None

def dump_outputs_autobackup(predicate, feedback_object, outputs_list):

    if predicate:
        return None

    warnings = None

    # get mvtools temp path
    v, r = mvtools_envvars.mvtools_envvar_read_temp_path()
    if not v:
        return "Cannot proceed with automatic backups - unable to retrieve mvtools's temporary path: [%s]" % r
    base_path = r

    for current_out in outputs_list:
        out_fn_pref, out_contents, out_log = current_out
        warnings = log_helper.add_to_warnings(warnings, dump_single_autobackup(feedback_object, base_path, out_fn_pref, out_contents, out_log))

    return warnings

if __name__ == "__main__":
    print("Hello from %s" % path_utils.basename_filtered(__file__))
