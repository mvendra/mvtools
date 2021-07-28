#!/usr/bin/env python3

import os

import path_utils
import maketimestamp
import mvtools_envvars

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
        if not v:

            v2, r2 = mvtools_envvars.mvtools_envvar_read_temp_path()
            if not v2:
                return False, "make_plugin failed: [%s]" % r2

            ts_now = maketimestamp.get_timestamp_now_compact()
            make_output_dump_filename = path_utils.concat_path(r2, "make_plugin_output_backup_%s.txt" % ts_now)
            if os.path.exists(make_output_dump_filename):
                return False, "make_plugin failed - output dump file [%s] already exists" % make_output_dump_filename

            with open(make_output_dump_filename, "w") as f:
                f.write(r)
            feedback_object("make failed - output was saved to [%s]" % make_output_dump_filename)

        if r is not None and suppress_make_output:
            r = "make's output was suppressed"
        return v, r
