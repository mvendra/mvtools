#!/usr/bin/env python3

import os

import launch_jobs

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "mklink"

    def _read_params(self):

        source_path = None
        target_path = None

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
            return False, "mklink failed - source path [%s] does not exist" % source_path

        if os.path.exists(target_path):
            return False, "mklink failed - target path [%s] already exists" % target_path

        return True, (source_path, target_path)

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        source_path, target_path = r

        # actual execution
        try:
            os.symlink(source_path, target_path)
        except:
            return False, "mklink failed - unable to create symlink from [%s] to [%s]" % (source_path, target_path)

        # post-verification
        if not os.path.exists(target_path):
            return False, "mklink failed - symlink from [%s] to [%s] was not created" % (source_path, target_path)

        # normal return
        return True, None
