#!/usr/bin/env python3

import os

import launch_jobs

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "mkdir"

    def run_task(self, execution_name=None):

        ignore_pre_existence = "ignore_pre_existence" in self.params

        try:
            target_folder = self.params["target_folder"]
        except KeyError:
            return False, "mkdir failed - target_folder is a required parameter"

        if not os.path.exists(target_folder):

            try:
                os.mkdir(target_folder)
            except FileNotFoundError as ex:
                return False, "mkdir failed - unable to create folder [%s]" % target_folder

            if not os.path.exists(target_folder):
                return False, "mkdir failed - unable to create folder [%s]" % target_folder
        else:
            if not ignore_pre_existence:
                return False, "mkdir failed - unable to create folder [%s] because it already exists" % target_folder

        return True, None
