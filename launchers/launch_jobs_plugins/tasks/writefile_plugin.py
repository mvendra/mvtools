#!/usr/bin/env python

import os

import path_utils

import launch_jobs

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "writefile"

    def _read_params(self):

        target_file = None
        mode = None
        content = None

        # target_file
        try:
            target_file = self.params["target_file"]
        except KeyError:
            return False, "target_file is a required parameter"

        # mode
        try:
            mode = self.params["mode"]
        except KeyError:
            pass # optional

        # content
        try:
            content = self.params["content"]
        except KeyError:
            return False, "content is a required parameter"

        return True, (target_file, mode, content)

    def run_task(self, feedback_object, execution_name=None):

        # read params
        v, r = self._read_params()
        if not v:
            return False, r
        target_file, mode, content = r

        with open(target_file, mode) as f:
            f.write(content)

        return True, None
