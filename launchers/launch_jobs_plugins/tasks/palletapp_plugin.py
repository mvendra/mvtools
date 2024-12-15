#!/usr/bin/env python3

import os

import launch_jobs
import path_utils
import palletapp_wrapper

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "palletapp"

    def _read_params(self):

        operation = None
        source_path = None
        target_path = None

        # operation
        try:
            operation = self.params["operation"]
        except KeyError:
            return False, "operation is a required parameter"

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

        return True, (operation, source_path, target_path)

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        operation, source_path, target_path = r

        # delegate
        if operation == "create":
            return self.task_create_package(feedback_object, source_path, target_path)
        elif operation == "extract":
            return self.task_extract_package(feedback_object, source_path, target_path)
        else:
            return False, "Operation [%s] is invalid" % operation

    def task_create_package(self, feedback_object, source_path, target_path):

        if source_path is None:
            return False, "No source path specified for task_create_package"

        if not os.path.exists(source_path):
            return False, "Source path [%s] does not exist" % source_path

        if target_path is None:
            return False, "No target archive specified for task_create_package"

        if os.path.exists(target_path):
            return False, "Target archive [%s] already exists" % target_path

        v, r = palletapp_wrapper.create(source_path, target_path)
        if not v:
            return False, r

        return True, None

    def task_extract_package(self, feedback_object, source_path, target_path):

        if source_path is None:
            return False, "No source archive specified for task_extract_package"

        if not os.path.exists(source_path):
            return False, "Source archive [%s] does not exist" % source_path

        if target_path is None:
            return False, "No target path specified for task_extract_package"

        if not os.path.exists(target_path):
            return False, "Target path [%s] does not exist" % target_path

        v, r = palletapp_wrapper.extract(source_path, target_path)
        if not v:
            return False, r

        return True, None
