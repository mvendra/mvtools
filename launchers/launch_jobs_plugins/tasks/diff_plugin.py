#!/usr/bin/env python3

import os

import launch_jobs
import path_utils

import diff_wrapper

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "diff"

    def _read_params(self):

        left_path = None
        right_path = None
        pass_mode = None

        # left_path
        try:
            left_path = self.params["left_path"]
        except KeyError:
            return False, "left_path is a required parameter"

        # right_path
        try:
            right_path = self.params["right_path"]
        except KeyError:
            return False, "right_path is a required parameter"

        # pass_mode
        try:
            pass_mode = self.params["pass_mode"]
        except KeyError:
            return False, "pass_mode is a required parameter"

        # params validation
        if not pass_mode in ["eq", "ne"]:
            return False, "pass_mode [%s] is invalid" % pass_mode

        return True, (left_path, right_path, pass_mode)

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        left_path, right_path, pass_mode = r

        v, r = diff_wrapper.do_diff(left_path, right_path)
        if not v:
            return False, r
        contents = r

        if pass_mode == "eq":
            if len(contents) > 0:
                return False, "contents of [%s] and [%s] are not equal" % (left_path, right_path)
        elif pass_mode == "ne":
            if len(contents) == 0:
                return False, "contents of [%s] and [%s] are equal" % (left_path, right_path)

        return True, None
