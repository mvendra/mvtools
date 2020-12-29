#!/usr/bin/env python3

import launch_jobs

class CustomTask(launch_jobs.BaseTask):
    def __init__(self, params=None):
        self.params = params
    def get_desc(self):
        return "sample_echo_false"
    def run_task(self):
        return False, None
