#!/usr/bin/env python3

import os

import launch_jobs
import path_utils
import fsquery
import format_list_str

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "check_dir_contents"

    def _read_params(self):

        target_path = None
        has_only = None
        nothing = None
        has_list = None
        not_list = None

        # target_path
        try:
            target_path = self.params["target_path"]
        except KeyError:
            return False, "target_path is a required parameter"

        # has_only
        try:
            has_only_read = self.params["has_only"]
            if isinstance(has_only_read, list):
                has_only = has_only_read
            else:
                has_only = []
                has_only.append(has_only_read)
        except KeyError:
            pass # optional

        # nothing
        if "nothing" in self.params:
            nothing = True

        # has
        try:
            has_list_read = self.params["has"]
            if isinstance(has_list_read, list):
                has_list = has_list_read
            else:
                has_list = []
                has_list.append(has_list_read)
        except KeyError:
            pass # optional

        # not
        try:
            not_list_read = self.params["not"]
            if isinstance(not_list_read, list):
                not_list = not_list_read
            else:
                not_list = []
                not_list.append(not_list_read)
        except KeyError:
            pass # optional

        # pre-validate params
        if not os.path.exists(target_path):
            return False, "target path [%s] does not exist" % target_path

        if not os.path.isdir(target_path):
            return False, "target path [%s] is not a folder" % target_path

        if (has_only is None) and (nothing is None) and (has_list is None) and (not_list is None):
            return False, "no checks selected"

        if has_only is not None:
            if (nothing is not None) or (has_list is not None) or (not_list is not None):
                return False, "has_only cannot be selected with anything else"

        if nothing is not None:
            if (has_only is not None) or (has_list is not None) or (not_list is not None):
                return False, "nothing cannot be selected with anything else"

        return True, (target_path, has_only, has_list, not_list)

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        target_path, has_only, has_list, not_list = r

        report = []

        v, r = fsquery.makecontentlist(target_path, False, False, True, True, True, True, True, None)
        if not v:
            return False, r
        all_files = [path_utils.basename_filtered(x) for x in r]

        # has_only
        if has_only is not None:

            found_keepers = 0
            for f in all_files:
                if f in has_only:
                    found_keepers += 1
                else:
                    report.append("[%s] is unexpectedly contained on [%s] (has-only)" % (f, target_path))

            if found_keepers == 0:
                report.append("found none of the [%s] expected on [%s] (has-only)" % (len(has_only), target_path))
            elif found_keepers != len(has_only):
                report.append("found only [%s] out of [%s] expected on [%s] (has-only)" % (found_keepers, len(has_only), target_path))

        else:

            # has
            if has_list is not None:
                for h in has_list:
                    if not h in all_files:
                        report.append("[%s] was expected on [%s] (has)" % (h, target_path))

            # not
            if not_list is not None:
                for h in not_list:
                    if h in all_files:
                        report.append("[%s] is unexpectedly contained on [%s] (not)" % (h, target_path))

        final_msg = None
        if len(report) > 0:
            final_msg = report
        return (len(report) == 0), format_list_str.format_list_str(final_msg, ". ")
