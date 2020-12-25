#!/usr/bin/env python3

import launch_jobs

class CustomStep(launch_jobs.BaseStep):
    def __init__(self, params=None):
        self.params = params
    def get_desc(self):
        return "sample_echo_false"
    def run_step(self):
        return False, None
