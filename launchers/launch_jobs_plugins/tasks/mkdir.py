#!/usr/bin/env python3

import os

import launch_jobs

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "mkdir"

    def run_task(self, feedback_object, execution_name=None):

        ignore_pre_existence = "ignore_pre_existence" in self.params

        try:
            target_path = self.params["target_path"]
        except KeyError:
            return False, "mkdir failed - target_path is a required parameter"

        if not os.path.exists(target_path):

            try:
                os.mkdir(target_path)
            except FileNotFoundError as ex:
                return False, "mkdir failed - unable to create folder [%s]" % target_path

            if not os.path.exists(target_path):
                return False, "mkdir failed - unable to create folder [%s]" % target_path
        else:
            if not ignore_pre_existence:
                return False, "mkdir failed - unable to create folder [%s] because it already exists" % target_path

        return True, None
