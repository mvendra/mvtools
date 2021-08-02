#!/usr/bin/env python3

import os

import launch_jobs
import path_utils

import svn_lib
import port_svn_repo
import reset_svn_repo
import apply_svn_patch

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "svn"

    def _read_params(self):

        target_path = None
        operation = None
        source_url = None
        source_path = None
        port_repo_head = False
        port_repo_unversioned = False
        port_repo_previous_count = None
        reset_files = None
        patch_head_file = None
        patch_unversioned_base = None
        patch_unversioned_file = None

        # target_path
        try:
            target_path = self.params["target_path"]
        except KeyError:
            return False, "target_path is a required parameter"

        # operation
        try:
            operation = self.params["operation"]
        except KeyError:
            return False, "operation is a required parameter"

        # source_url
        try:
            source_url = self.params["source_url"]
        except KeyError:
            pass # optional

        # source_path
        try:
            source_path = self.params["source_path"]
        except KeyError:
            pass # optional

        # port_repo_head
        try:
            port_repo_head = self.params["port_repo_head"]
            port_repo_head = True
        except KeyError:
            pass # optional

        # port_repo_unversioned
        try:
            port_repo_unversioned = self.params["port_repo_unversioned"]
            port_repo_unversioned = True
        except KeyError:
            pass # optional

        # port_repo_previous_count
        try:
            port_repo_previous_count = self.params["port_repo_previous_count"]
        except KeyError:
            pass # optional

        # reset_file
        try:
            reset_files = self.params["reset_file"]
        except KeyError:
            pass # optional

        # patch_head_file
        try:
            patch_head_file = self.params["patch_head_file"]
        except KeyError:
            pass # optional

        # patch_unversioned_base
        try:
            patch_unversioned_base = self.params["patch_unversioned_base"]
        except KeyError:
            pass # optional

        # patch_unversioned_file
        try:
            patch_unversioned_file = self.params["patch_unversioned_file"]
        except KeyError:
            pass # optional

        return True, (target_path, operation, source_url, source_path, port_repo_head, port_repo_unversioned, port_repo_previous_count, reset_files, patch_head_file, patch_unversioned_base, patch_unversioned_file)

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        target_path, operation, source_url, source_path, port_repo_head, port_repo_unversioned, port_repo_previous_count, reset_files, patch_head_files, patch_unversioned_base, patch_unversioned_files = r

        # delegate
        if operation == "checkout_repo":
            return self.task_checkout_repo(feedback_object, source_url, target_path)
        elif operation == "update_repo":
            return self.task_update_repo(feedback_object, target_path)
        elif operation == "port_repo":
            return self.task_port_repo(feedback_object, source_path, target_path, port_repo_head, port_repo_unversioned, port_repo_previous_count)
        elif operation == "reset_repo":
            return self.task_reset_repo(feedback_object, target_path)
        elif operation == "reset_file":
            return self.task_reset_file(feedback_object, target_path, reset_files)
        elif operation == "patch_repo":
            return self.task_patch_repo(feedback_object, target_path, patch_head_files, patch_unversioned_base, patch_unversioned_files)
        elif operation == "check_repo":
            return self.task_check_repo(feedback_object, target_path)
        else:
            return False, "Operation [%s] is invalid" % operation

    def task_checkout_repo(self, feedback_object, source_url, target_path):

        if source_url is None:
            return False, "Source URL is required port task_checkout_repo"

        if os.path.exists(target_path):
            return False, "Target path [%s] already exists" % target_path

        warnings = None
        v, r = svn_lib.checkout_autoretry(feedback_object, source_url, target_path, True)
        if not v:
            return False, r
        if r is not None:
            warnings = r

        if not os.path.exists(target_path):
            return False, "svn checkout failed - unable to checkout into [%s]" % (target_path)

        return True, warnings

    def task_update_repo(self, feedback_object, target_path):

        if not os.path.exists(target_path):
            return False, "Target path [%s] does not exist" % target_path

        warnings = None

        v, r = svn_lib.update_autorepair(target_path, True, True)
        if not v:
            return False, r

        if r is not None:
            warnings = r

        return True, warnings

    def task_port_repo(self, feedback_object, source_path, target_path, port_repo_head, port_repo_unversioned, port_repo_previous_count):

        if source_path is None:
            return False, "Source path (source_path) is required port task_port_repo"
        if not os.path.exists(source_path):
            return False, "Source path [%s] does not exist" % source_path

        if not os.path.exists(target_path):
            return False, "Target path [%s] does not exist" % target_path

        if port_repo_previous_count is None:
            port_repo_previous_count = "0"
        if not port_repo_previous_count.isnumeric():
            return False, "Invalid previous_count - expected numeric string: [%s]" % port_repo_previous_count
        port_repo_previous_count = int(port_repo_previous_count)

        v, r = port_svn_repo.port_svn_repo(source_path, target_path, port_repo_head, port_repo_unversioned, port_repo_previous_count)
        if not v:
            return False, r

        return True, None

    def task_reset_repo(self, feedback_object, target_path):

        if not os.path.exists(target_path):
            return False, "Target path [%s] does not exist" % target_path

        v, r = reset_svn_repo.reset_svn_repo(target_path, None)
        if not v:
            return False, r
        backed_up_patches = r

        for w in backed_up_patches:
            feedback_object(w)

        warning_msg = None
        if len(backed_up_patches) > 0:
            warning_msg = "Backups were made"

        return True, warning_msg

    def task_reset_file(self, feedback_object, target_path, reset_files):

        if not os.path.exists(target_path):
            return False, "Target path [%s] does not exist" % target_path

        if not isinstance(reset_files, list) and reset_files is not None:
            reset_files = [reset_files]

        if reset_files is None:
            return False, "No files were specified for resetting"

        if not isinstance(reset_files, list):
            return False, "reset_files must be a list"

        v, r = reset_svn_repo.reset_svn_repo(target_path, reset_files)
        if not v:
            return False, r
        backed_up_patches = r

        for w in backed_up_patches:
            feedback_object(w)

        warning_msg = None
        if len(backed_up_patches) > 0:
            warning_msg = "Backups were made"

        return True, warning_msg

    def task_patch_repo(self, feedback_object, target_path, patch_head_files, patch_unversioned_base, patch_unversioned_files):

        # apply_svn_patch supports different unversioned_bases per unversioned_file
        # but in this plugin, we only allow one unversioned_base for all unversioned_file items
        # this is because it would be a much bigger complication to allow one custom base per file
        # because that would require more parsing from dsl type20.
        # to compensate, unversioned_file entries should be specified without a fullpath

        if not os.path.exists(target_path):
            return False, "Target path [%s] does not exist" % target_path

        if not isinstance(patch_head_files, list) and patch_head_files is not None:
            patch_head_files = [patch_head_files]
        elif patch_head_files is None:
            patch_head_files = []

        if not isinstance(patch_unversioned_files, list) and patch_unversioned_files is not None:
            patch_unversioned_files = [patch_unversioned_files]
        elif patch_unversioned_files is None:
            patch_unversioned_files = []

        if patch_unversioned_base is not None:
            if not os.path.exists(patch_unversioned_base):
                return False, "Unversioned base path [%s] does not exist" % patch_unversioned_base

        unversioned_patches = []
        for puf in patch_unversioned_files:
            unversioned_patches.append( (patch_unversioned_base, path_utils.concat_path(patch_unversioned_base, puf)) )

        v, r = apply_svn_patch.apply_svn_patch(target_path, patch_head_files, unversioned_patches)
        if not v:
            return False, r

        return True, None

    def task_check_repo(self, feedback_object, target_path):

        if not os.path.exists(target_path):
            return False, "Target path [%s] does not exist" % target_path

        v, r = svn_lib.is_head_clear(target_path, True)
        if not v:
            return False, "svn_lib failed: [%s]" % r

        if not r:
            return False, "Target path's [%s] head is not clear" % target_path

        return True, None
