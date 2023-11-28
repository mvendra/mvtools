#!/usr/bin/env python3

import os

import launch_jobs
import path_utils
import mv_wrapper

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "mv"

    def _read_params(self):

        source_path = None
        target_path = None

        # source_path
        try:
            source_path = self.params["source_path"]
        except KeyError:
            return False, "source_path is a required parameter"

        # target_path
        try:
            target_path = self.params["target_path"]
        except KeyError:
            return False, "target_path is a required parameter"

        # validations
        if not os.path.exists(source_path):
            return False, "Source path [%s] does not exist" % source_path

        # renaming is *not* allowed
        if not os.path.exists(target_path):
            return False, "Target path [%s] does not exist" % target_path

        if not os.path.isdir(target_path):
            return False, "Target path [%s] must be a folder" % target_path

        final_path = path_utils.concat_path(target_path, path_utils.basename_filtered(source_path))
        if os.path.exists(final_path):
            return False, "Final path [%s] already exists" % final_path

        return True, (source_path, target_path)

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        source_path, target_path = r

        v, r = mv_wrapper.move(source_path, target_path)
        if not v:
            return False, r
        return True, None
