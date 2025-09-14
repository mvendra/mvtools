#!/usr/bin/env python

import os

import path_utils
import launch_jobs

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "scratchfolder"

    def run_task(self, feedback_object, execution_name=None):

        try:
            target_path = self.params["target_path"]
        except KeyError:
            return False, "scratchfolder failed - target_path is a required parameter"

        r = path_utils.scratchfolder(target_path)
        if not r:
            return False, "scratchfolder for path [%s] failed" % target_path

        return True, None
