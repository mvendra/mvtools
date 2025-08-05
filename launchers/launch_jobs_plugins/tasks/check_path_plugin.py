#!/usr/bin/env python3

import os

import launch_jobs
import format_list_str

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "check_path"

    def _read_params(self):

        path_file_exist = None
        path_dir_exist = None
        path_not_exist = None

        # path_file_exist
        try:
            path_file_exist_read = self.params["path_file_exist"]
            if isinstance(path_file_exist_read, list):
                path_file_exist = path_file_exist_read
            else:
                path_file_exist = []
                path_file_exist.append(path_file_exist_read)
        except KeyError:
            pass # optional

        # path_dir_exist
        try:
            path_dir_exist_read = self.params["path_dir_exist"]
            if isinstance(path_dir_exist_read, list):
                path_dir_exist = path_dir_exist_read
            else:
                path_dir_exist = []
                path_dir_exist.append(path_dir_exist_read)
        except KeyError:
            pass # optional

        # path_not_exist
        try:
            path_not_exist_read = self.params["path_not_exist"]
            if isinstance(path_not_exist_read, list):
                path_not_exist = path_not_exist_read
            else:
                path_not_exist = []
                path_not_exist.append(path_not_exist_read)
        except KeyError:
            pass # optional

        # pre-validate params
        if path_file_exist is None and path_dir_exist is None and path_not_exist is None:
            return False, "no parameters specified"

        return True, (path_file_exist, path_dir_exist, path_not_exist)

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        path_file_exist, path_dir_exist, path_not_exist = r

        report = []

        # path_file_exist
        if path_file_exist is not None:
            for p in path_file_exist:
                if not os.path.exists(p):
                    report.append("[%s] does not exist" % p)
                    continue
                if os.path.isdir(p):
                    report.append("[%s] exists but is a directory" % p)

        # path_dir_exist
        if path_dir_exist is not None:
            for p in path_dir_exist:
                if not os.path.exists(p):
                    report.append("[%s] does not exist" % p)
                    continue
                if not os.path.isdir(p):
                    report.append("[%s] exists but is not a directory" % p)

        # path_not_exist
        if path_not_exist is not None:
            for p in path_not_exist:
                if os.path.exists(p):
                    report.append("[%s] exists" % p)

        final_msg = None
        if len(report) > 0:
            final_msg = report
        return (len(report) == 0), format_list_str.format_list_str(final_msg, ". ")
