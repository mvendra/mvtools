#!/usr/bin/env python3

import launch_jobs

class CustomStep(launch_jobs.BaseStep):
    def __init__(self, params=None):
        self.params = params
    def get_desc(self):
        return "sample_echo_true"
    def run_step(self):
        return True, None
