#!/usr/bin/env python3

import os

import launch_jobs

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "check_envvars"

    def run_task(self, feedback_object, execution_name=None):

        # envvars
        list_envvars = []
        try:
            list_envvars_read = self.params["envvar"]
            if isinstance(list_envvars_read, list):
                list_envvars = list_envvars_read
            else:
                list_envvars.append(list_envvars_read)
        except KeyError:
            pass # optional

        if len(list_envvars) == 0:
            return False, "check_envvars failed: nothing to check."

        for ev in list_envvars:
            if not ev in os.environ:
                return False, "check_envvars failed: envvar [%s] is not defined." % ev

        return True, None
