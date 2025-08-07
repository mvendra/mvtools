#!/usr/bin/env python3

import os

import path_utils
import log_helper
import output_backup_helper

import launch_jobs
import make_wrapper

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "make"

    def _read_params(self):

        work_dir = None
        jobs = None
        target = None
        prefix = None
        save_output = None
        filter_output = None
        save_error_output = None
        filter_error_output = None
        suppress_stderr_warnings = None

        # work_dir
        try:
            work_dir = self.params["work_dir"]
        except KeyError:
            return False, "work_dir is a required parameter"

        # jobs
        try:
            jobs = self.params["jobs"]
        except KeyError:
            pass # optional

        # target
        try:
            target = self.params["target"]
        except KeyError:
            pass # optional

        # prefix
        try:
            prefix = self.params["prefix"]
        except KeyError:
            pass # optional

        # save_output
        try:
            save_output = self.params["save_output"]
        except KeyError:
            pass # optional

        # filter_output
        try:
            filter_output = self.params["filter_output"]
        except KeyError:
            pass # optional

        # save_error_output
        try:
            save_error_output = self.params["save_error_output"]
        except KeyError:
            pass # optional

        # filter_error_output
        try:
            filter_error_output = self.params["filter_error_output"]
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

        return True, (work_dir, jobs, target, prefix, save_output, filter_output, save_error_output, filter_error_output, suppress_stderr_warnings)

    def run_task(self, feedback_object, execution_name=None):

        warnings = None

        # read params
        v, r = self._read_params()
        if not v:
            return False, r
        work_dir, jobs, target, prefix, save_output, filter_output, save_error_output, filter_error_output, suppress_stderr_warnings = r

        # actual execution
        v, r = make_wrapper.make(work_dir, jobs, target, prefix)
        if not v:
            return False, r
        proc_result = r[0]
        proc_stdout = r[1]
        proc_stderr = r[2]

        # dump outputs
        output_backup_helper.dump_output(feedback_object, save_output, proc_stdout, ("Make's stdout has been saved to: [%s]" % save_output))
        output_backup_helper.dump_output(feedback_object, save_error_output, proc_stderr, ("Make's stderr has been saved to: [%s]" % save_error_output))

        # filter outputs
        # mvtodo

        # autobackup outputs
        output_list = [("make_plugin_stdout", proc_stdout, "Make's stdout"), ("make_plugin_stderr", proc_stderr, "Make's stderr")]
        warnings = log_helper.add_to_warnings(warnings, output_backup_helper.dump_outputs_autobackup(proc_result, feedback_object, output_list))

        # warnings
        if len(proc_stderr) > 0:
            if not suppress_stderr_warnings:
                warnings = log_helper.add_to_warnings(warnings, proc_stderr)
            else:
                warnings = log_helper.add_to_warnings(warnings, "make's stderr has been suppressed")
        return True, warnings
