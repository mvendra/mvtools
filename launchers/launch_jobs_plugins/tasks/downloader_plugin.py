#!/usr/bin/env python3

import os

import launch_jobs

import download_url

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "downloader"

    def run_task(self, feedback_object, execution_name=None):

        try:
            source_url = self.params["source_url"]
        except KeyError:
            return False, "downloader failed - source_url is a required parameter"

        try:
            target_path = self.params["target_path"]
        except KeyError:
            return False, "downloader failed - target_path is a required parameter"

        if os.path.exists(target_path):
            return False, "downloader failed - file [%s] already exists." % target_path

        v, r = download_url.download_url(source_url, target_path)
        if not v:
            return False, "downloader failed: [%s]" % r

        return True, None
