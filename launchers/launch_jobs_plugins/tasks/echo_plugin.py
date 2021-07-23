#!/usr/bin/env python3

import launch_jobs
import maketimestamp

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "echo"

    def run_task(self, feedback_object, execution_name=None):

        message = None

        # message
        try:
            message = self.params["message"]
        except KeyError:
            return False, "message is a required parameter"

        timestamp_now = maketimestamp.get_timestamp_now()

        print("[%s]: %s" % (timestamp_now, message))

        return True, None
