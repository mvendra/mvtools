#!/usr/bin/env python3

import os

import path_utils
import log_helper
import output_backup_helper

import launch_jobs
import bazel_wrapper

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "bazel"

    def _read_params(self):

        exec_path = None
        operation = None
        jobs = None
        config = None
        target = None
        expunge = False
        fail_test_fail_task = False
        options = []
        arguments = []
        save_output = None
        save_error_output = None
        suppress_stderr_warnings = None

        # exec_path
        try:
            exec_path = self.params["exec_path"]
        except KeyError:
            return False, "exec_path is a required parameter"

        # operation
        try:
            operation = self.params["operation"]
        except KeyError:
            return False, "operation is a required parameter"

        # jobs
        try:
            jobs = self.params["jobs"]
            if not isinstance(jobs, str):
                return False, "jobs is expected once at most"
        except KeyError:
            pass # optional

        # config
        try:
            config = self.params["config"]
            if not isinstance(config, str):
                return False, "config is expected once at most"
        except KeyError:
            pass # optional

        # target
        try:
            target = self.params["target"]
        except KeyError:
            pass # optional

        # expunge
        expunge = "expunge" in self.params

        # fail_test_fail_task
        fail_test_fail_task = "fail_test_fail_task" in self.params

        # options
        try:
            options_read = self.params["opt"]
            if isinstance(options_read, list):
                options = options_read
            else:
                options.append(options_read)
        except KeyError:
            pass # optional

        # arguments
        try:
            arguments_read = self.params["arg"]
            if isinstance(arguments_read, list):
                arguments = arguments_read
            else:
                arguments.append(arguments_read)
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

        # validate exec_path
        if not os.path.exists(exec_path):
            return False, "exec_path [%s] does not exist." % exec_path

        # suppress_stderr_warnings
        suppress_stderr_warnings = "suppress_stderr_warnings" in self.params

        # save_output
        if save_output is not None:
            if os.path.exists(save_output):
                return False, "save_output [%s] points to a preexisting path" % save_output

        # save_error_output
        if save_error_output is not None:
            if os.path.exists(save_error_output):
                return False, "save_error_output [%s] points to a preexisting path" % save_error_output

        return True, (exec_path, operation, jobs, config, target, expunge, fail_test_fail_task, options, arguments, save_output, save_error_output, suppress_stderr_warnings)

    def run_task(self, feedback_object, execution_name=None):

        # read params
        v, r = self._read_params()
        if not v:
            return False, r
        exec_path, operation, jobs, config, target, expunge, fail_test_fail_task, options, arguments, save_output, save_error_output, suppress_stderr_warnings = r

        # delegate
        if operation == "build":
            return self.task_build(feedback_object, exec_path, jobs, config, target, options, save_output, save_error_output, suppress_stderr_warnings)
        elif operation == "fetch":
            return self.task_fetch(feedback_object, exec_path, target, save_output, save_error_output, suppress_stderr_warnings)
        elif operation == "clean":
            return self.task_clean(feedback_object, exec_path, expunge, save_output, save_error_output, suppress_stderr_warnings)
        elif operation == "run":
            return self.task_run(feedback_object, exec_path, target, arguments, save_output, save_error_output, suppress_stderr_warnings)
        elif operation == "test":
            return self.task_test(feedback_object, exec_path, jobs, config, target, fail_test_fail_task, options, save_output, save_error_output, suppress_stderr_warnings)
        else:
            return False, "Operation [%s] is invalid" % operation

    def task_build(self, feedback_object, exec_path, jobs, config, target, options, save_output, save_error_output, suppress_stderr_warnings):

        warnings = None

        # actual execution
        v, r = bazel_wrapper.build(exec_path, jobs, config, target, options)
        if not v:
            return False, r
        proc_result = r[0]
        proc_stdout = r[1]
        proc_stderr = r[2]

        # dump outputs
        output_backup_helper.dump_output(feedback_object, save_output, proc_stdout, ("Bazel's stdout has been saved to: [%s]" % save_output))
        output_backup_helper.dump_output(feedback_object, save_error_output, proc_stderr, ("Bazel's stderr has been saved to: [%s]" % save_error_output))

        # autobackup outputs
        output_list = [("bazel_plugin_stdout", proc_stdout, "Bazel's stdout"), ("bazel_plugin_stderr", proc_stderr, "Bazel's stderr")]
        warnings = log_helper.add_to_warnings(warnings, output_backup_helper.dump_outputs_autobackup(proc_result, feedback_object, output_list))

        # warnings
        if len(proc_stderr) > 0:
            if not suppress_stderr_warnings:
                warnings = log_helper.add_to_warnings(warnings, proc_stderr)
            else:
                warnings = log_helper.add_to_warnings(warnings, "bazel's stderr has been suppressed")
        return True, warnings

    def task_fetch(self, feedback_object, exec_path, target, save_output, save_error_output, suppress_stderr_warnings):

        warnings = None

        # actual execution
        v, r = bazel_wrapper.fetch(exec_path, target)
        if not v:
            return False, r
        proc_result = r[0]
        proc_stdout = r[1]
        proc_stderr = r[2]

        # dump outputs
        output_backup_helper.dump_output(feedback_object, save_output, proc_stdout, ("Bazel's stdout has been saved to: [%s]" % save_output))
        output_backup_helper.dump_output(feedback_object, save_error_output, proc_stderr, ("Bazel's stderr has been saved to: [%s]" % save_error_output))

        # autobackup outputs
        output_list = [("bazel_plugin_stdout", proc_stdout, "Bazel's stdout"), ("bazel_plugin_stderr", proc_stderr, "Bazel's stderr")]
        warnings = log_helper.add_to_warnings(warnings, output_backup_helper.dump_outputs_autobackup(proc_result, feedback_object, output_list))

        # warnings
        if len(proc_stderr) > 0:
            if not suppress_stderr_warnings:
                warnings = log_helper.add_to_warnings(warnings, proc_stderr)
            else:
                warnings = log_helper.add_to_warnings(warnings, "bazel's stderr has been suppressed")
        return True, warnings

    def task_clean(self, feedback_object, exec_path, expunge, save_output, save_error_output, suppress_stderr_warnings):

        warnings = None

        # actual execution
        v, r = bazel_wrapper.clean(exec_path, expunge)
        if not v:
            return False, r
        proc_result = r[0]
        proc_stdout = r[1]
        proc_stderr = r[2]

        # dump outputs
        output_backup_helper.dump_output(feedback_object, save_output, proc_stdout, ("Bazel's stdout has been saved to: [%s]" % save_output))
        output_backup_helper.dump_output(feedback_object, save_error_output, proc_stderr, ("Bazel's stderr has been saved to: [%s]" % save_error_output))

        # autobackup outputs
        output_list = [("bazel_plugin_stdout", proc_stdout, "Bazel's stdout"), ("bazel_plugin_stderr", proc_stderr, "Bazel's stderr")]
        warnings = log_helper.add_to_warnings(warnings, output_backup_helper.dump_outputs_autobackup(proc_result, feedback_object, output_list))

        # warnings
        if len(proc_stderr) > 0:
            if not suppress_stderr_warnings:
                warnings = log_helper.add_to_warnings(warnings, proc_stderr)
            else:
                warnings = log_helper.add_to_warnings(warnings, "bazel's stderr has been suppressed")
        return True, warnings

    def task_run(self, feedback_object, exec_path, target, arguments, save_output, save_error_output, suppress_stderr_warnings):

        warnings = None

        # actual execution
        v, r = bazel_wrapper.run(exec_path, target, arguments)
        if not v:
            return False, r
        proc_result = r[0]
        proc_stdout = r[1]
        proc_stderr = r[2]

        # dump outputs
        output_backup_helper.dump_output(feedback_object, save_output, proc_stdout, ("Bazel's stdout has been saved to: [%s]" % save_output))
        output_backup_helper.dump_output(feedback_object, save_error_output, proc_stderr, ("Bazel's stderr has been saved to: [%s]" % save_error_output))

        # autobackup outputs
        output_list = [("bazel_plugin_stdout", proc_stdout, "Bazel's stdout"), ("bazel_plugin_stderr", proc_stderr, "Bazel's stderr")]
        warnings = log_helper.add_to_warnings(warnings, output_backup_helper.dump_outputs_autobackup(proc_result, feedback_object, output_list))

        # warnings
        if len(proc_stderr) > 0:
            if not suppress_stderr_warnings:
                warnings = log_helper.add_to_warnings(warnings, proc_stderr)
            else:
                warnings = log_helper.add_to_warnings(warnings, "bazel's stderr has been suppressed")
        return True, warnings

    def task_test(self, feedback_object, exec_path, jobs, config, target, fail_test_fail_task, options, save_output, save_error_output, suppress_stderr_warnings):

        warnings = None

        # actual execution
        v, r = bazel_wrapper.test(exec_path, jobs, config, target, options)
        if not v:
            return False, r
        proc_result = r[0]
        proc_stdout = r[1]
        proc_stderr = r[2]

        # dump outputs
        output_backup_helper.dump_output(feedback_object, save_output, proc_stdout, ("Bazel's stdout has been saved to: [%s]" % save_output))
        output_backup_helper.dump_output(feedback_object, save_error_output, proc_stderr, ("Bazel's stderr has been saved to: [%s]" % save_error_output))

        # autobackup outputs
        output_list = [("bazel_plugin_stdout", proc_stdout, "Bazel's stdout"), ("bazel_plugin_stderr", proc_stderr, "Bazel's stderr")]
        warnings = log_helper.add_to_warnings(warnings, output_backup_helper.dump_outputs_autobackup(proc_result, feedback_object, output_list))

        # warnings
        if len(proc_stderr) > 0:
            if not suppress_stderr_warnings:
                warnings = log_helper.add_to_warnings(warnings, proc_stderr)
            else:
                warnings = log_helper.add_to_warnings(warnings, "bazel's stderr has been suppressed")

        ret = True
        if fail_test_fail_task and not proc_result:
            ret = False
        return ret, warnings
