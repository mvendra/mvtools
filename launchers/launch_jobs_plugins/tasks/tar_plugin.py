#!/usr/bin/env python

import os

import launch_jobs
import path_utils
import tar_wrapper
import bzip2_wrapper

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "tar"

    def _read_params(self):

        operation = None
        target_archive = None
        source_path = None
        target_path = None
        compress = None

        # operation
        try:
            operation = self.params["operation"]
        except KeyError:
            return False, "operation is a required parameter"

        # target_archive
        try:
            target_archive = self.params["target_archive"]
        except KeyError:
            return False, "target_archive is a required parameter"

        # source_path
        try:
            source_path = self.params["source_path"]
        except KeyError:
            pass # optional

        # target_path
        try:
            target_path = self.params["target_path"]
        except KeyError:
            pass # optional

        # compress
        compress = "compress" in self.params

        return True, (operation, target_archive, source_path, target_path, compress)

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        operation, target_archive, source_path, target_path, compress = r

        # delegate
        if operation == "create":
            return self.task_create_package(feedback_object, target_archive, source_path, compress)
        elif operation == "extract":
            return self.task_extract_package(feedback_object, target_archive, target_path)
        elif operation == "compress":
            return self.task_compress_package(feedback_object, target_archive)
        else:
            return False, "Operation [%s] is invalid" % operation

    def task_create_package(self, feedback_object, target_archive, source_path, compress):

        if target_archive is None:
            return False, "Target archive is required for task_create_package"

        if os.path.exists(target_archive):
            return False, "Target archive [%s] already exists" % target_archive

        if source_path is None:
            return False, "No source paths specified for task_create_package"

        item_list = []
        if not isinstance(source_path, list):
            item_list.append(source_path)
        else:
            item_list = source_path

        for it in item_list:
            if not os.path.exists(it):
                return False, "Source path [%s] does not exist" % it

        v, r = tar_wrapper.make_pack(target_archive, item_list)
        if not v:
            return False, r

        if compress:
            v, r = bzip2_wrapper.compress(target_archive)
            if not v:
                return False, r

        return True, None

    def task_extract_package(self, feedback_object, target_archive, target_path):

        if not os.path.exists(target_archive):
            return False, "Target archive [%s] does not exist" % target_archive

        if target_path is None:
            return False, "Target path is required for task_extract_package"

        if not os.path.exists(target_path):
            return False, "Target path [%s] does not exist" % target_path

        v, r = tar_wrapper.extract(target_archive, target_path)
        if not v:
            return False, r

        return True, None

    def task_compress_package(self, feedback_object, target_archive):

        if not os.path.exists(target_archive):
            return False, "Target archive [%s] does not exist" % target_archive

        v, r = bzip2_wrapper.compress(target_archive)
        if not v:
            return False, r

        return True, None
