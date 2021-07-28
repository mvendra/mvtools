#!/usr/bin/env python3

import os

import launch_jobs
import make_wrapper

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "make"

    def run_task(self, feedback_object, execution_name=None):

        work_dir = None
        target = None
        save_output = None
        suppress_make_output = False

        # work_dir
        try:
            work_dir = self.params["work_dir"]
        except KeyError:
            return False, "make failed - work_dir is a required parameter"

        # target
        try:
            target = self.params["target"]
        except KeyError:
            pass # optional

        # suppress_make_output
        if "suppress_make_output" in self.params:
            suppress_make_output = True

        # save_output
        try:
            save_output = self.params["save_output"]
        except KeyError:
            pass # optional

        # pre-validate parameters
        if not os.path.exists(work_dir):
            return False, "make failed - work_dir [%s] does not exist." % work_dir

        # save_output
        if save_output is not None:
            if os.path.exists(save_output):
                return False, "make_plugin: save_output [%s] points to a preexisting path" % save_output

        v, r = make_wrapper.make(work_dir, suppress_make_output, target)
        if save_output is not None:
            with open(save_output, "w") as f:
                f.write(r)
            feedback_object("Make's output has been saved to: [%s]" % save_output)
        if r is not None and suppress_make_output:
            r = "make's output was suppressed"
        return v, r
