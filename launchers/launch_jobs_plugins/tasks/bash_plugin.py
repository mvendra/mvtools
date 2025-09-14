#!/usr/bin/env python

import os

import path_utils
import log_helper
import output_backup_helper

import launch_jobs
import bash_wrapper

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "bash"

    def _read_params(self):

        script = None
        cwd = None
        args = []
        save_output = None
        save_error_output = None
        suppress_stderr_warnings = None

        # script
        try:
            script = self.params["script"]
        except KeyError:
            return False, "script is a required parameter"

        # cwd
        try:
            cwd = self.params["cwd"]
        except KeyError:
            pass # optional

        # args
        try:
            args_read = self.params["arg"]
            if isinstance(args_read, list):
                args = args_read
            else:
                args.append(args_read)
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

        # validate script
        if not os.path.exists(script):
            return False, "script [%s] does not exist" % script

        # validate cwd
        if cwd is not None:
            if not os.path.exists(cwd):
                return False, "cwd [%s] does not exist" % cwd

        # validate save_output
        if save_output is not None:
            if os.path.exists(save_output):
                return False, "save_output [%s] points to a preexisting path" % save_output

        # validate save_error_output
        if save_error_output is not None:
            if os.path.exists(save_error_output):
                return False, "save_error_output [%s] points to a preexisting path" % save_error_output

        return True, (script, cwd, args, save_output, save_error_output, suppress_stderr_warnings)

    def run_task(self, feedback_object, execution_name=None):

        # read params
        v, r = self._read_params()
        if not v:
            return False, r
        script, cwd, args, save_output, save_error_output, suppress_stderr_warnings = r

        # actual execution
        v, r = bash_wrapper.exec(script, cwd, args)
        if not v:
            return False, r
        proc_result = r[0]
        proc_stdout = r[1]
        proc_stderr = r[2]

        warnings = None

        # dump outputs
        output_backup_helper.dump_output(feedback_object, save_output, proc_stdout, ("Bash's stdout has been saved to: [%s]" % save_output))
        output_backup_helper.dump_output(feedback_object, save_error_output, proc_stderr, ("Bash's stderr has been saved to: [%s]" % save_error_output))

        # autobackup outputs
        output_list = [("bash_plugin_stdout", proc_stdout, "Bash's stdout"), ("bash_plugin_stderr", proc_stderr, "Bash's stderr")]
        warnings = log_helper.add_to_warnings(warnings, output_backup_helper.dump_outputs_autobackup(proc_result, feedback_object, output_list))

        # warnings
        if len(proc_stderr) > 0:
            if not suppress_stderr_warnings:
                warnings = log_helper.add_to_warnings(warnings, proc_stderr)
            else:
                warnings = log_helper.add_to_warnings(warnings, "bash's stderr has been suppressed")
        return True, warnings
