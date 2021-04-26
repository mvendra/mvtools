#!/usr/bin/env python3

import os

import launch_jobs
import svn_lib

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "svn"

    def run_task(self, feedback_object, execution_name=None):

        # operation
        try:
            operation = self.params["operation"]
        except KeyError:
            return False, "svn failed - operation is a required parameter"

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
        elif operation == "revert":
            return self.run_task_revert(target_path)
        else:
            return False, "svn failed - operation [%s] is invalid" % operation

    def run_task_checkout(self, target_path):

        warnings = None

        # pre-check
        if os.path.exists(target_path):
            return False, "svn checkout failed - target path [%s] already exists" % target_path

        # remote_link
        try:
            remote_link = self.params["remote_link"]
        except KeyError:
            return False, "svn checkout failed - remote_link is a required parameter"

        # actual execution
        v, r = svn_lib.checkout_autorepair(remote_link, target_path)
        if not v:
            return False, r

        if r is not None:
            # succeeded, but warnings were issued
            warnings = r

        # post-verification
        if not os.path.exists(target_path):
            return False, "svn checkout failed - unable to checkout into [%s]" % (target_path)

        # normal return
        return True, warnings

    def run_task_update(self, target_path):

        warnings = None

        # pre-check
        if not os.path.exists(target_path):
            return False, "svn update failed - target path [%s] does not exist" % target_path

        # actual execution
        v, r = svn_lib.update_autorepair(target_path, True)
        if not v:
            return False, r

        if r is not None:
            # succeeded, but warnings were issued
            warnings = r

        # normal return
        return True, warnings

    def run_task_revert(self, target_path):

        warnings = None
        repo_item = None

        # pre-check
        if not os.path.exists(target_path):
            return False, "svn revert failed - target path [%s] does not exist" % target_path

        # repo_item
        try:
            repo_item = self.params["repo_item"]
        except KeyError:
            pass # its optional

        # actual execution
        v, r = svn_lib.revert(target_path, repo_item)
        if not v:
            return False, r

        if r is not None:
            # succeeded, but warnings were issued
            warnings = r

        # normal return
        return True, warnings
