#!/usr/bin/env python

import os

import launch_jobs
import path_utils
import get_platform

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "check_platform"

    def _read_params(self):

        expected = None

        # expected
        try:
            expected_read = self.params["expected"]
            if not isinstance(expected_read, list):
                expected = []
                expected.append(expected_read)
            else:
                expected = expected_read
        except KeyError:
            pass # optional

        return True, expected

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        expected = r

        local_plat = get_platform.getplat()

        if expected is None:
            expected = []
            expected.append(local_plat)

        if not local_plat in expected:
            return False, "Local platform [%s] is not expected" % local_plat

        return True, None
