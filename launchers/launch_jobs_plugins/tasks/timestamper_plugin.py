#!/usr/bin/env python3

import os

import launch_jobs
import maketimestamp

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "timestamper"

    def run_task(self, feedback_object, execution_name=None):

        try:
            target_filename = self.params["target_filename"]
        except KeyError:
            return False, "timestamper failed - target_filename is a required parameter"

        message = None
        try:
            message = self.params["message"]
        except KeyError:
            pass # optional

        if os.path.exists(target_filename):
            return False, "timestamper failed - file [%s] already exists." % target_filename

        timestamp_now = maketimestamp.get_timestamp_now()

        full_contents = ""
        full_contents += timestamp_now + os.linesep
        if message is not None:
            full_contents += message

        with open(target_filename, "w") as f:
            f.write(full_contents)

        return True, None
