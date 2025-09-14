#!/usr/bin/env python

import os

import launch_jobs
import path_utils

import generic_run

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "generic_run"

    def _read_params(self):

        command = None
        cwd = None
        args = None

        # command
        try:
            command = self.params["command"]
        except KeyError:
            return False, "command is a required parameter"

        # cwd
        try:
            cwd = self.params["cwd"]
        except KeyError:
            pass # optional

        # args
        try:
            arg_read = self.params["arg"]
            if isinstance(arg_read, list):
                args = arg_read
            else:
                args = [arg_read]
        except KeyError:
            pass # optional

        return True, (command, cwd, args)

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        command, cwd, args = r

        final_cmd = []
        final_cmd.append(command)

        if args is not None:
            for a in args:
                final_cmd.append(a)

        v, r = generic_run.run_cmd_simple(final_cmd, use_cwd=cwd)
        if not v:
            return False, "Running command [%s] failed: [%s]" % (final_cmd, r)

        return True, None
