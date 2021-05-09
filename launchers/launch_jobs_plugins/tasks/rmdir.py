#!/usr/bin/env python3

import os

import launch_jobs
import path_utils

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "rmdir"

    def run_task(self, feedback_object, execution_name=None):

        ignore_non_pre_existence = "ignore_non_pre_existence" in self.params

        try:
            target_path = self.params["target_path"]
        except KeyError:
            return False, "rmdir failed - target_path is a required parameter"

        if not os.path.exists(target_path) and not ignore_non_pre_existence:
            return False, "rmdir failed - target_path does not exist"

        path_utils.deletefolder_ignoreerrors(target_path)

        return True, None
