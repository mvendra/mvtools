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
        default_filter = None
        filter_include = None
        filter_exclude = None
        port_head = False
        port_unversioned = False
        port_previous_count = None
        port_cherry_pick_previous = None
        reset_head = False
        reset_unversioned = False
        reset_previous_count = None
        patch_head_file = None
        patch_unversioned_base = None
        patch_unversioned_file = None
        check_head_include_externals = False
        check_head_ignore_unversioned = False
        rewind_to_rev = None
        rewind_like_source = False

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

        # default_filter
        try:
            default_filter = self.params["default_filter"]
        except KeyError:
            pass # optional

        # filter_include
        try:
            filter_include = []
            filter_include_read = self.params["filter_include"]
            if isinstance(filter_include_read, list):
                filter_include = filter_include_read
            else:
                filter_include.append(filter_include_read)
        except KeyError:
            pass # optional

        # filter_exclude
        try:
            filter_exclude = []
            filter_exclude_read = self.params["filter_exclude"]
            if isinstance(filter_exclude_read, list):
                filter_exclude = filter_exclude_read
            else:
                filter_exclude.append(filter_exclude_read)
        except KeyError:
            pass # optional

        # port_head
        try:
            port_head = self.params["port_head"]
            port_head = True
        except KeyError:
            pass # optional

        # port_unversioned
        try:
            port_unversioned = self.params["port_unversioned"]
            port_unversioned = True
        except KeyError:
            pass # optional

        # port_previous_count
        try:
            port_previous_count = self.params["port_previous_count"]
        except KeyError:
            pass # optional

        # port_cherry_pick_previous
        try:
            port_cherry_pick_previous = self.params["port_cherry_pick_previous"]
        except KeyError:
            pass # optional

        # reset_head
        try:
            reset_head = self.params["reset_head"]
            reset_head = True
        except KeyError:
            pass # optional

        # reset_unversioned
        try:
            reset_unversioned = self.params["reset_unversioned"]
            reset_unversioned = True
        except KeyError:
            pass # optional

        # reset_previous_count
        try:
            reset_previous_count = self.params["reset_previous_count"]
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

        # check_head_include_externals
        try:
            check_head_include_externals = self.params["check_head_include_externals"]
            check_head_include_externals = True
        except KeyError:
            pass # optional

        # check_head_ignore_unversioned
        try:
            check_head_ignore_unversioned = self.params["check_head_ignore_unversioned"]
            check_head_ignore_unversioned = True
        except KeyError:
            pass # optional

        # rewind_to_rev
        try:
            rewind_to_rev = self.params["rewind_to_rev"]
        except KeyError:
            pass # optional

        # rewind_like_source
        try:
            rewind_like_source = self.params["rewind_like_source"]
            rewind_like_source = True
        except KeyError:
            pass # optional

        return True, (target_path, operation, source_url, source_path, default_filter, filter_include, filter_exclude, port_head, port_unversioned, port_previous_count, port_cherry_pick_previous, reset_head, reset_unversioned, reset_previous_count, patch_head_file, patch_unversioned_base, patch_unversioned_file, check_head_include_externals, check_head_ignore_unversioned, rewind_to_rev, rewind_like_source)

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        target_path, operation, source_url, source_path, default_filter, filter_include, filter_exclude, port_head, port_unversioned, port_previous_count, port_cherry_pick_previous, reset_head, reset_unversioned, reset_previous_count, patch_head_files, patch_unversioned_base, patch_unversioned_files, check_head_include_externals, check_head_ignore_unversioned, rewind_to_rev, rewind_like_source = r

        # delegate
        if operation == "checkout_repo":
            return self.task_checkout_repo(feedback_object, source_url, target_path)
        elif operation == "update_repo":
            return self.task_update_repo(feedback_object, target_path)
        elif operation == "port_repo":
            return self.task_port_repo(feedback_object, source_path, target_path, default_filter, filter_include, filter_exclude, port_head, port_unversioned, port_previous_count, port_cherry_pick_previous)
        elif operation == "reset_repo":
            return self.task_reset_repo(feedback_object, target_path, default_filter, filter_include, filter_exclude, reset_head, reset_unversioned, reset_previous_count)
        elif operation == "rewind_repo":
            return self.task_rewind_repo(feedback_object, target_path, source_path, rewind_to_rev, rewind_like_source)
        elif operation == "patch_repo":
            return self.task_patch_repo(feedback_object, target_path, patch_head_files, patch_unversioned_base, patch_unversioned_files)
        elif operation == "check_repo":
            return self.task_check_repo(feedback_object, target_path, check_head_include_externals, check_head_ignore_unversioned)
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

        v, r = svn_lib.update_autorepair(feedback_object, target_path, True, True)
        if not v:
            return False, r

        if r is not None:
            warnings = r

        return True, warnings

    def task_port_repo(self, feedback_object, source_path, target_path, default_filter, filter_include, filter_exclude, port_head, port_unversioned, port_previous_count, port_cherry_pick_previous):

        if source_path is None:
            return False, "Source path (source_path) is required port task_port_repo"
        if not os.path.exists(source_path):
            return False, "Source path [%s] does not exist" % source_path

        if not os.path.exists(target_path):
            return False, "Target path [%s] does not exist" % target_path

        if port_previous_count is None:
            port_previous_count = "0"
        if not port_previous_count.isnumeric():
            return False, "Invalid previous_count - expected numeric string: [%s]" % port_previous_count
        port_previous_count = int(port_previous_count)

        v, r = port_svn_repo.port_svn_repo(source_path, target_path, default_filter, filter_include, filter_exclude, port_head, port_unversioned, port_previous_count, port_cherry_pick_previous)
        if not v:
            return False, r
        port_repo_output = r

        warning_msg = None
        if port_repo_output is not None:
            if len(port_repo_output) > 0 :
                warning_msg = "port_svn_repo has produced output"
            for o in port_repo_output:
                feedback_object(o)

        return True, warning_msg

    def task_reset_repo(self, feedback_object, target_path, default_filter, filter_include, filter_exclude, reset_head, reset_unversioned, reset_previous_count):

        if not os.path.exists(target_path):
            return False, "Target path [%s] does not exist" % target_path

        if reset_previous_count is None:
            reset_previous_count = "0"
        if not reset_previous_count.isnumeric():
            return False, "Invalid previous_count - expected numeric string: [%s]" % reset_previous_count
        reset_previous_count = int(reset_previous_count)

        v, r = reset_svn_repo.reset_svn_repo(target_path, default_filter, filter_include, filter_exclude, reset_head, reset_unversioned, reset_previous_count)
        if not v:
            return False, r
        backed_up_patches = r

        for w in backed_up_patches:
            feedback_object(w)

        warning_msg = None
        if len(backed_up_patches) > 0:
            warning_msg = "reset_svn_repo has produced output"

        return True, warning_msg

    def task_rewind_repo(self, feedback_object, target_path, source_path, rewind_to_rev, rewind_like_source):

        if not os.path.exists(target_path):
            return False, "Target path [%s] does not exist" % target_path

        if (rewind_to_rev is not None) and rewind_like_source:
            return False, "rewind_repo should receive either rewind_to_rev xor rewind_like_source - never both at the same time."

        if rewind_like_source:

            if source_path is None:
                return False, "Source path (source_path) is required for task_rewind_repo (when passed rewind_like_source)"
            if not os.path.exists(source_path):
                return False, "Source path [%s] does not exist" % source_path

            v, r = svn_lib.get_head_revision(source_path)
            if not v:
                return False, "Unable to retrieve head revision of source path [%s]: [%s]" % (source_path, r)
            rewind_to_rev = r

        if rewind_to_rev is None:
            return False, "No revision to rewind to (target_path: [%s])" % target_path

        v, r = svn_lib.get_previous_list(target_path)
        if not v:
            return False, "Unable to retrieve previous revision list of target path [%s]: [%s]" % (target_path, r)
        prev_revs = r

        c = 0
        found = False
        for pri in prev_revs:

            if rewind_to_rev == pri:
                found = True
                break

            c += 1

        if not found:
            return False, "Failed attempting to rewind repo [%s]: Revision [%s] was not found (hint: revision numbers must be prefixed with 'r' - example: 'r355')" % (source_path, rewind_to_rev)

        v, r = reset_svn_repo.reset_svn_repo(target_path, "include", [], [], False, False, c)
        if not v:
            return False, r
        backed_up_patches = r

        for w in backed_up_patches:
            feedback_object(w)

        warning_msg = None
        if len(backed_up_patches) > 0:
            warning_msg = "reset_svn_repo has produced output"

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

    def task_check_repo(self, feedback_object, target_path, include_externals, ignore_unversioned):

        if not os.path.exists(target_path):
            return False, "Target path [%s] does not exist" % target_path

        v, r = svn_lib.is_head_clear(target_path, include_externals, ignore_unversioned)
        if not v:
            return False, "svn_lib failed: [%s]" % r

        if not r:
            return False, "Target path's [%s] head is not clear" % target_path

        return True, None
