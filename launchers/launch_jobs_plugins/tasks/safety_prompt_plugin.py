#!/usr/bin/env python

import launch_jobs

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "safety_prompt"

    def _read_params(self):

        message = None

        try:
            message = self.params["msg"]
        except KeyError:
            return False, "msg is a required parameter"

        return True, (message)

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        message = r

        feedback_object("")
        feedback_object(message)
        answer = input("Input your answer (yes / no): ")
        if answer != "yes":
            return False, "safety_prompt failed: the provided answer was in the negative: [%s]" % answer

        return True, None
