#!/usr/bin/env python3

import os

import launch_jobs

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "mklink"

    def run_task(self, execution_name=None):

        # source_path
        try:
            source_path = self.params["source_path"]
        except KeyError:
            return False, "mklink failed - source_path is a required parameter"

        # target_path
        try:
            target_path = self.params["target_path"]
        except KeyError:
            return False, "mklink failed - target_path is a required parameter"

        # pre-checks
        if not os.path.exists(source_path):
            return False, "mkdir failed - source path [%s] does not exist" % source_path
        if os.path.exists(target_path):
            return False, "mkdir failed - target path [%s] already exists" % target_path

        # actual execution
        try:
            os.symlink(source_path, target_path)
        except FileNotFoundError as ex:
            return False, "mkdir failed - unable to create symlink from [%s] to [%s]" % (source_path, target_path)

        # post-verification
        if not os.path.exists(target_path):
            return False, "mkdir failed - unable to create symlink from [%s] to [%s]" % (source_path, target_path)

        # normal return
        return True, None
