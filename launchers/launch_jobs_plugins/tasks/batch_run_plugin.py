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
        op_mode = None
        op_mode_arg = None
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

        # op_mode
        try:
            op_mode = self.params["op_mode"]
        except KeyError:
            return False, "op_mode is a required parameter"

        # op_mode_arg
        try:
            op_mode_arg = self.params["op_mode_arg"]
        except KeyError:
            pass # optional

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

        # validations
        target = os.path.abspath(target)
        if not os.path.exists(target):
            return False, "Target [%s] does not exist." % target

        output = os.path.abspath(output)
        if os.path.exists(output):
            return False, "Output [%s] already exists." % output

        valid_op_modes = ["until-fail", "until-num", "until-sig"]
        if not op_mode in valid_op_modes:
            return False, "Operation mode [%s] is invalid." % op_mode

        op_modes_require_arg = ["until-num", "until-sig"]
        if op_mode in op_modes_require_arg and op_mode_arg is None:
            return False, "Operation mode [%s] requires an argument." % op_mode

        valid_same_modes = ["save-all", "save-fail"]
        if not save_mode in valid_same_modes:
            return False, "Save mode [%s] is invalid." % save_mode

        return True, (target, output, op_mode, op_mode_arg, save_mode, target_args)

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        target, output, op_mode, op_mode_arg, save_mode, target_args = r

        v, r = batch_run.batch_run(target, output, op_mode, op_mode_arg, save_mode, target_args)
        if not v:
            return False, "Batch run failed: [%s]." % r

        return True, None
