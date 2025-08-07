#!/usr/bin/env python3

import os

import launch_jobs
import path_utils

import plug_filter

import diff_wrapper

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "diff"

    def _read_params(self):

        left_path = None
        right_path = None
        right_filter = None
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

        # right_filter
        try:
            right_filter_read = self.params["right_filter"]
            if isinstance(right_filter_read, list):
                right_filter = right_filter_read
            else:
                right_filter = []
                right_filter.append(right_filter_read)
        except KeyError:
            pass # optional

        # mode
        try:
            mode = self.params["mode"]
        except KeyError:
            return False, "mode is a required parameter"

        # params validation
        if not mode in ["eq-fail", "eq-warn", "ne-fail", "ne-warn"]:
            return False, "mode [%s] is invalid" % mode

        return True, (left_path, right_path, right_filter, mode)

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        left_path, right_path, right_filter, mode = r

        v, r = diff_wrapper.do_diff(left_path, plug_filter.plug_filter(right_filter, right_path))
        if not v:
            return False, r
        contents = r

        # mvtodo: inform about filters being used or not
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
