#!/usr/bin/env python3

import os

import launch_jobs
import path_utils

import batch_run

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "batch_run"

    def _read_params(self):

        target = None
        output = None
        op_modes = []
        op_modes_args = []
        save_mode = None
        target_args = []

        # target
        try:
            target = self.params["target"]
        except KeyError:
            return False, "target is a required parameter"

        # output
        try:
            output = self.params["output"]
        except KeyError:
            return False, "output is a required parameter"

        # op_modes
        try:
            op_modes_read = self.params["op_modes"]
            if isinstance(op_modes_read, list):
                op_modes = op_modes_read
            else:
                op_modes = [op_modes_read]
        except KeyError:
            return False, "op_modes is a required parameter"

        # op_modes_args
        try:
            op_modes_args_read = self.params["op_modes_args"]
            if isinstance(op_modes_args_read, list):
                op_modes_args = op_modes_args_read
            else:
                op_modes_args = [op_modes_args_read]
        except KeyError:
            return False, "op_modes_args is a required parameter"

        # save_mode
        try:
            save_mode = self.params["save_mode"]
        except KeyError:
            return False, "save_mode is a required parameter"

        # target_args
        try:
            target_args_read = self.params["target_args"]
            if isinstance(target_args_read, list):
                target_args = target_args_read
            else:
                target_args = [target_args_read]
        except KeyError:
            pass # optional

        if len(op_modes) != len(op_modes_args):
            return False, "op_modes and op_modes_args must match in length"

        return True, (target, output, op_modes, op_modes_args, save_mode, target_args)

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        target, output, op_modes, op_modes_args, save_mode, target_args = r

        op_modes_final = []
        for i in range(len(op_modes)):
            op_modes_final.append([op_modes[i], op_modes_args[i]])

        v, r = batch_run.batch_run(target, output, op_modes_final, save_mode, target_args)
        if not v:
            return False, "Batch run failed: [%s]." % r

        return True, None
