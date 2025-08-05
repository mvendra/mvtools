#!/usr/bin/env python3

import os

import launch_jobs
import path_utils
import fsquery
import format_list_str

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "cleanup_dir"

    def _read_params(self):

        target_path = None
        keep_only = None
        ditch = None

        # target_path
        try:
            target_path = self.params["target_path"]
        except KeyError:
            return False, "target_path is a required parameter"

        # keep_only
        try:
            keep_only = self.params["keep_only"]
        except KeyError:
            pass # optional

        # ditch
        try:
            ditch_read = self.params["ditch"]
            if isinstance(ditch_read, list):
                ditch = ditch_read
            else:
                ditch = []
                ditch.append(ditch_read)
        except KeyError:
            pass # optional

        # pre-validate params
        if not os.path.exists(target_path):
            return False, "target path [%s] does not exist" % target_path

        if not os.path.isdir(target_path):
            return False, "target path [%s] is not a folder" % target_path

        if (keep_only is None) and (ditch is None):
            return False, "no operations selected"

        if (keep_only is not None) and (ditch is not None):
            return False, "keep_only cannot be selected with ditch"

        return True, (target_path, keep_only, ditch)

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        target_path, keep_only, ditch = r

        report = []

        v, r = fsquery.makecontentlist(target_path, False, False, True, True, True, True, True, None)
        if not v:
            return False, r
        all_files = r

        # keep_only
        if keep_only is not None:

            found_keeper = False
            for f in all_files:
                if path_utils.basename_filtered(f) == keep_only:
                    found_keeper = True
                    continue
                if not path_utils.remove_path(f):
                    return False, "could not remove [%s] (keep-only)" % f

            if not found_keeper:
                report.append("[%s] was not found on [%s] (keep-only)" % (keep_only, target_path))

        else: # ditch

            for fd in ditch:
                found = False
                for fa in all_files:
                    if fd == path_utils.basename_filtered(fa):
                        if not path_utils.remove_path(fa):
                            return False, "could not remove [%s] (ditch)" % fa
                        found = True
                        break
                if not found:
                    report.append("[%s] was not found on [%s] (ditch)" % (fd, target_path))

        final_msg = None
        if len(report) > 0:
            final_msg = report
        return True, format_list_str.format_list_str(final_msg, ". ")
