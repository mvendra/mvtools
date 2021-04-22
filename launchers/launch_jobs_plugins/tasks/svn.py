#!/usr/bin/env python3

import os

import launch_jobs
import svn_lib

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "svn"

    def run_task(self, execution_name=None):

        # operation
        try:
            operation = self.params["operation"]
        except KeyError:
            return False, "svn failed - operation is a required parameter"
        if operation != "checkout" and operation != "update":
            return False, "svn failed - operation [%s] is invalid" % operation

        # target_path
        try:
            target_path = self.params["target_path"]
        except KeyError:
            return False, "svn failed - target_path is a required parameter"

        # delegate
        if operation == "checkout":
            return self.run_task_checkout(target_path)
        elif operation == "update":
            return self.run_task_update(target_path)

    def run_task_checkout(self, target_path):

        print("mvdebug checkout")

        # pre-check
        if os.path.exists(target_path):
            return False, "svn failed - target path [%s] already exists" % target_path

        # remote_link
        try:
            remote_link = self.params["remote_link"]
        except KeyError:
            return False, "svn failed - remote_link is a required parameter"

        # actual execution
        v, r = svn_lib.checkout_autoretry(remote_link, target_path)
        if not v:
            return False, r

        # post-verification
        if not os.path.exists(target_path):
            return False, "svn failed - unable to checkout into [%s]" % (target_path)

        # normal return
        return True, None

    def run_task_update(self, target_path):

        print("mvdebug update")

        # pre-check
        if not os.path.exists(target_path):
            return False, "svn failed - target path [%s] does not exist" % target_path

        v, r = svn_lib.update_autoretry(target_path)
        if not v:
            return False, r

        # normal return
        return True, None
