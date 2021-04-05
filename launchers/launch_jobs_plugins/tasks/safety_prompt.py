#!/usr/bin/env python3

import launch_jobs

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "safety_prompt"

    def run_task(self, execution_name=None):

        try:
            message = self.params["msg"]
        except KeyError:
            return False, "safety_prompt failed - msg is a required parameter"

        print("")
        print(message)
        answer = input("Input your answer (yes/no):")
        if answer != "yes":
            return False, "safety_prompt failed: the provided answer was in the negative: [%s]" % answer

        return True, None
