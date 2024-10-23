#!/usr/bin/env python3

import os

import launch_jobs
import path_utils

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "patcher"

    def _read_params(self):

        target_path = None
        target_index = None
        target_len = None
        source = None

        # target_path
        try:
            target_path = self.params["target_path"]
        except KeyError:
            return False, "target_path is a required parameter"

        # target_index
        try:
            target_index = self.params["target_index"]
        except KeyError:
            return False, "target_index is a required parameter"

        # target_len
        try:
            target_len = self.params["target_len"]
        except KeyError:
            return False, "target_len is a required parameter"

        # source
        try:
            source = self.params["source"]
        except KeyError:
            return False, "source is a required parameter"

        return True, (target_path, target_index, target_len, source)

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        target_path, target_index, target_len, source = r

        if not os.path.exists(target_path):
            return False, "target_path [%s] does not exist" % target_path

        if os.path.isdir(target_path):
            return False, "target_path [%s] is a folder" % target_path

        contents = ""
        with open(target_path) as f:
            contents = f.read()

        target_index = int(target_index)
        target_len = int(target_len)

        if target_len == 0:
            return False, "target_len [%s] cannot be zero" % target_len

        final_pos = target_index+target_len

        if (final_pos) > len(contents):
            return False, "target_index [%s] plus target_len [%s] go past the content's total length [%s]" % (target_index, target_len, len(contents))

        new_contents = contents[0:target_index] + source + contents[target_index+target_len:]

        os.remove(target_path)

        with open(target_path, "w") as f:
            f.write(new_contents)

        return True, None
