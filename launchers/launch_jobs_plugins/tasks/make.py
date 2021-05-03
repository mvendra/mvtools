#!/usr/bin/env python3

import os

import launch_jobs
import make_wrapper

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "make"

    def run_task(self, feedback_object, execution_name=None):

        # work_dir
        try:
            work_dir = self.params["work_dir"]
        except KeyError:
            return False, "make failed - work_dir is a required parameter"

        # target
        target = None
        try:
            target = self.params["target"]
        except KeyError:
            pass # optional

        # suppress_make_output
        suppress_make_output = False
        if "suppress_make_output" in self.params:
            suppress_make_output = True

        # pre-validate parameters
        if not os.path.exists(work_dir):
            return False, "make failed - work_dir [%s] does not exist." % work_dir

        v, r = make_wrapper.make(work_dir, target)
        if r is not None and suppress_make_output:
            r = "make's output was suppressed"
        return v, r
