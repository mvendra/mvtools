#!/usr/bin/env python

import launch_jobs

class CustomTask(launch_jobs.BaseTask):
    def get_desc(self):
        return "sample_echo_false"
    def run_task(self, feedback_object, execution_name=None):
        return False, None
