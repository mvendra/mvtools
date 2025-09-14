#!/usr/bin/env python

import os

import launch_jobs
import path_utils

import tree_wrapper

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "tree"

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

        # params validation
        if not os.path.exists(source_path):
            return False, "source_path [%s] does not exist." % source_path

        if os.path.exists(target_path):
            return False, "target_path [%s] already exists." % target_path

        return True, (source_path, target_path)

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        source_path, target_path = r

        v, r = tree_wrapper.make_tree(source_path)
        if not v:
            return False, r
        contents = r

        with open(target_path, "w") as f:
            f.write(contents)

        return True, None
