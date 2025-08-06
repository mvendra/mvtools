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
        keep = None
        ditch = None

        # target_path
        try:
            target_path = self.params["target_path"]
        except KeyError:
            return False, "target_path is a required parameter"

        # keep
        try:
            keep_read = self.params["keep"]
            if isinstance(keep_read, list):
                keep = keep_read
            else:
                keep = []
                keep.append(keep_read)
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

        if (keep is None) and (ditch is None):
            return False, "no operations selected"

        if (keep is not None) and (ditch is not None):
            return False, "either keep or ditch must be used - not both"

        return True, (target_path, keep, ditch)

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        target_path, keep, ditch = r

        report = []

        v, r = fsquery.makecontentlist(target_path, False, False, True, True, True, True, True, None)
        if not v:
            return False, r
        all_files = r

        # keep
        if keep is not None:

            found_keepers = 0
            for f in all_files:
                if path_utils.basename_filtered(f) in keep:
                    found_keepers += 1
                    continue
                if not path_utils.remove_path(f):
                    return False, "could not remove [%s] (keep-only)" % f

            if found_keepers == 0:
                report.append("found none of the [%s] expected on [%s] (keep-only)" % (len(keep), target_path))
            elif found_keepers != len(keep):
                report.append("found only [%s] out of [%s] expected on [%s] (keep-only)" % (found_keepers, len(keep), target_path))

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
