#!/usr/bin/env python3

import os

import launch_jobs
import path_utils

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "copy"

    def _read_params(self):

        source_path = None
        target_path = None
        rename_to = None

        # source_path
        try:
            source_path = self.params["source_path"]
        except KeyError:
            return False, "source_path is a required parameter"

        # target_path
        try:
            target_path = self.params["target_path"]
        except KeyError:
            return False, "target_path is a required parameter"

        # rename_to
        try:
            rename_to = self.params["rename_to"]
        except KeyError:
            pass # optional

        return True, (source_path, target_path, rename_to)

    def run_task(self, feedback_object, execution_name=None):

        # examples:
        #
        # first case:
        # source_path = "/usr/source/file1.txt"
        # target_path = "/usr/target"
        # rename_to = None
        # result: "/usr/target/file1.txt"
        #
        # second case:
        # source_path = "/usr/source/file1.txt"
        # target_path = "/usr/target"
        # rename_to = "file2.txt"
        # result: "/usr/target/file2.txt"

        v, r = self._read_params()
        if not v:
            return False, r
        source_path, target_path, rename_to = r

        if not os.path.exists(source_path):
            return False, "source_path [%s] does not exist." % source_path

        if not os.path.exists(target_path):
            return False, "target_path [%s] does not exist." % target_path

        if rename_to is not None:
            final_path = path_utils.concat_path(target_path, rename_to)
            if os.path.exists(final_path):
                return False, "Final path [%s] already exists." % final_path

        if rename_to is None:

            # copy without renaming. remember: the name is part of the copying of the object.
            v = path_utils.copy_to(source_path, target_path)
            if not v:
                return False, "Copying [%s] to [%s] failed." % (source_path, target_path)

        else:

            # copy with renaming
            v = path_utils.copy_to_and_rename(source_path, target_path, rename_to)
            if not v:
                return False, "Copying [%s] to [%s] with new name [%s] failed." % (source_path, target_path, rename_to)

        return True, None
