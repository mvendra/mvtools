#!/usr/bin/env python3

import os

import path_utils
import maketimestamp
import mvtools_envvars
import log_helper

import launch_jobs
import make_wrapper

def _dump_output(feedback_object, name_log, output_filename, output_contents):

    if output_filename is not None:
        with open(output_filename, "w") as f:
            f.write(output_contents)
        feedback_object("Make's %s has been saved to: [%s]" % (name_log, output_filename))

def _dump_outputs_backup(feedback_object, stdout, stderr):

    warnings = None

    # get mvtools temp path
    v, r = mvtools_envvars.mvtools_envvar_read_temp_path()
    if not v:
        return False, r

    # get ts
    ts_now = maketimestamp.get_timestamp_now_compact()

    # output
    make_output_dump_filename = path_utils.concat_path(r, "make_plugin_output_backup_%s.txt" % ts_now)
    if not os.path.exists(make_output_dump_filename):
        with open(make_output_dump_filename, "w") as f:
            f.write(stdout)
        feedback_object("output was saved to [%s]" % make_output_dump_filename)
    else:
        warnings = log_helper.add_to_warnings(warnings, "output dump file [%s] already exists" % make_output_dump_filename)

    # error output
    make_error_output_dump_filename = path_utils.concat_path(r, "make_plugin_error_output_backup_%s.txt" % ts_now)
    if not os.path.exists(make_error_output_dump_filename):
        with open(make_error_output_dump_filename, "w") as f:
            f.write(stderr)
        feedback_object("error output was saved to [%s]" % make_error_output_dump_filename)
    else:
        warnings = log_helper.add_to_warnings(warnings, "error output dump file [%s] already exists" % make_error_output_dump_filename)

    return (warnings is None), warnings

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "make"

    def _read_params(self):

        work_dir = None
        target = None
        save_output = None
        save_error_output = None
        suppress_stderr_warnings = None

        # work_dir
        try:
            work_dir = self.params["work_dir"]
        except KeyError:
            return False, "work_dir is a required parameter"

        # target
        try:
            target = self.params["target"]
        except KeyError:
            pass # optional

        # save_output
        try:
            save_output = self.params["save_output"]
        except KeyError:
            pass # optional

        # save_error_output
        try:
            save_error_output = self.params["save_error_output"]
        except KeyError:
            pass # optional

        # suppress_stderr_warnings
        suppress_stderr_warnings = "suppress_stderr_warnings" in self.params

        # pre-validate parameters
        if not os.path.exists(work_dir):
            return False, "work_dir [%s] does not exist." % work_dir

        # save_output
        if save_output is not None:
            if os.path.exists(save_output):
                return False, "save_output [%s] points to a preexisting path" % save_output

        # save_error_output
        if save_error_output is not None:
            if os.path.exists(save_error_output):
                return False, "save_error_output [%s] points to a preexisting path" % save_error_output

        return True, (work_dir, target, save_output, save_error_output, suppress_stderr_warnings)

    def run_task(self, feedback_object, execution_name=None):

        warnings = None

        # read params
        v, r = self._read_params()
        if not v:
            return False, r
        work_dir, target, save_output, save_error_output, suppress_stderr_warnings = r

        # actual execution
        v, r = make_wrapper.make(work_dir, target)
        if not v:
            return False, r
        proc_result = r[0]
        proc_stdout = r[1]
        proc_stderr = r[2]

        # dump outputs
        _dump_output(feedback_object, "output", save_output, proc_stdout)
        _dump_output(feedback_object, "error output", save_error_output, proc_stderr)

        # backup outputs
        if not proc_result:
            v, r = _dump_outputs_backup(feedback_object, proc_stdout, proc_stderr)
            if not v:
                warnings = log_helper.add_to_warnings(warnings, r)

        # warnings
        if len(proc_stderr) > 0:
            if not suppress_stderr_warnings:
                warnings = log_helper.add_to_warnings(warnings, proc_stderr)
            else:
                warnings = log_helper.add_to_warnings(warnings, "make's stderr has been suppressed")
        return True, warnings
