#!/usr/bin/env python3

import os

import launch_jobs
import prjcleanup

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "prjcleanup"

    def _read_params(self):

        proj = None
        dep = None
        tmp = None
        out = None

        # proj
        try:
            proj = self.params["proj"]
        except KeyError:
            return False, "proj is a required parameter"

        # dep
        dep = "dep" in self.params

        # tmp
        tmp = "tmp" in self.params

        # out
        out = "out" in self.params

        if not os.path.exists(proj):
            return False, "proj [%s] points to a nonexistent path" % proj

        return True, (proj, dep, tmp, out)

    def run_task(self, feedback_object, execution_name=None):

        # read params
        v, r = self._read_params()
        if not v:
            return False, r
        proj, dep, tmp, out = r

        v, r = prjcleanup.prjcleanup(proj, dep, tmp, out)
        if not v:
            return False, "Task failed: [%s]" % r
        return True, None
