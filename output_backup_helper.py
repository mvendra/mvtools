#!/usr/bin/env python3

import sys
import os

import path_utils
import maketimestamp
import mvtools_envvars
import mvtools_exception
import log_helper

def dump_output(feedback_object, output_filename, output_contents, log_message):

    if output_filename is not None:

        if os.path.exists(output_filename):
            raise mvtools_exception.mvtools_exception("Output filename [%s] already exists." % output_filename)

        with open(output_filename, "w") as f:
            f.write(output_contents)
        feedback_object(log_message)

def dump_single_autobackup(feedback_object, base_path, output_fn_prefix, output_contents, output_log):

    # get ts
    ts_now = maketimestamp.get_timestamp_now_compact()

    output_filename = path_utils.concat_path(base_path, "%s_autobackup_%s.txt" % (output_fn_prefix, ts_now))
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
