#!/usr/bin/env python3

import os

import launch_jobs
import path_utils

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "rm"

    def _read_params(self):

        target_path = None
        ignore_non_pre_existence = "ignore_non_pre_existence" in self.params

        # target_path
        try:
            target_path = self.params["target_path"]
        except KeyError:
            return False, "target_path is a required parameter"

        return True, (target_path, ignore_non_pre_existence)

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        target_path, ignore_non_pre_existence = r

        if not os.path.exists(target_path):
            if ignore_non_pre_existence:
                return True, "target_path [%s] does not exist (ignored)" % target_path
            return False, "target_path [%s] does not exist" % target_path

        if os.path.isdir(target_path):
            return False, "target_path [%s] is a directory" % target_path

        os.unlink(target_path)

        return True, None
