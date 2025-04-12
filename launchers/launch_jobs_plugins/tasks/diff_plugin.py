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
        mode = None

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

        # mode
        try:
            mode = self.params["mode"]
        except KeyError:
            return False, "mode is a required parameter"

        # params validation
        if not mode in ["eq-fail", "eq-warn", "ne-fail", "ne-warn"]:
            return False, "mode [%s] is invalid" % mode

        return True, (left_path, right_path, mode)

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        left_path, right_path, mode = r

        v, r = diff_wrapper.do_diff(left_path, right_path)
        if not v:
            return False, r
        contents = r

        if mode == "eq-fail":
            if len(contents) == 0:
                return False, "contents of [%s] and [%s] are equal" % (left_path, right_path)
        elif mode == "eq-warn":
            if len(contents) == 0:
                return True, "contents of [%s] and [%s] are equal" % (left_path, right_path)
        elif mode == "ne-fail":
            if len(contents) > 0:
                return False, "contents of [%s] and [%s] are not equal" % (left_path, right_path)
        elif mode == "ne-warn":
            if len(contents) > 0:
                return True, "contents of [%s] and [%s] are not equal" % (left_path, right_path)

        return True, None
