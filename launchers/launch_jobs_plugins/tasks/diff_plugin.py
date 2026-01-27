#!/usr/bin/env python

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
        left_filter = None
        right_path = None
        right_filter = None
        mode = None

        # left_path
        try:
            left_path = self.params["left_path"]
        except KeyError:
            return False, "left_path is a required parameter"

        # left_filter
        try:
            left_filter_read = self.params["left_filter"]
            if isinstance(left_filter_read, list):
                left_filter = left_filter_read
            else:
                left_filter = []
                left_filter.append(left_filter_read)
        except KeyError:
            pass # optional

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
        if not os.path.exists(left_path):
            return False, "left source [%s] does not exist" % left_path

        if not os.path.exists(right_path):
            return False, "right source [%s] does not exist" % right_path

        if left_filter is not None:
            if not os.path.exists(left_filter[0]):
                return False, "left filter script [%s] does not exist" % left_filter[0]

        if right_filter is not None:
            if not os.path.exists(right_filter[0]):
                return False, "right filter script [%s] does not exist" % right_filter[0]

        if not mode in ["eq-fail", "eq-warn", "ne-fail", "ne-warn"]:
            return False, "mode [%s] is invalid" % mode

        return True, (left_path, left_filter, right_path, right_filter, mode)

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        left_path, left_filter, right_path, right_filter, mode = r

        left_filter_str = ""
        if left_filter is not None:
            left_filter_str = " (filtered)"

        right_filter_str = ""
        if right_filter is not None:
            right_filter_str = " (filtered)"

        v, r = diff_wrapper.do_diff(plug_filter.plug_filter(left_filter, left_path), plug_filter.plug_filter(right_filter, right_path))
        if not v:
            return False, r
        contents = r

        if mode == "eq-fail":
            if len(contents) == 0:
                return False, "contents of [%s%s] and [%s%s] are equal" % (left_path, left_filter_str, right_path, right_filter_str)
        elif mode == "eq-warn":
            if len(contents) == 0:
                return True, "contents of [%s%s] and [%s%s] are equal" % (left_path, left_filter_str, right_path, right_filter_str)
        elif mode == "ne-fail":
            if len(contents) > 0:
                return False, "contents of [%s%s] and [%s%s] are not equal" % (left_path, left_filter_str, right_path, right_filter_str)
        elif mode == "ne-warn":
            if len(contents) > 0:
                return True, "contents of [%s%s] and [%s%s] are not equal" % (left_path, left_filter_str, right_path, right_filter_str)

        return True, None
