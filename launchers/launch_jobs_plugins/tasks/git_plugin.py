#!/usr/bin/env python

import os

import launch_jobs
import path_utils
import log_helper
import output_backup_helper

import git_lib
import port_git_repo
import reset_git_repo
import apply_git_patch

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "git"

    def _read_params(self):

        target_path = None
        operation = None
        source_url = None
        remote_name = None
        branch_name = None
        source_path = None
        default_filter = None
        filter_include = None
        filter_exclude = None
        port_head = False
        port_staged = False
        port_stash_count = None
        port_unversioned = False
        port_previous_count = None
        port_cherry_pick_previous = None
        reset_head = False
        reset_staged = False
        reset_stash_count = None
        reset_unversioned = False
        reset_previous_count = None
        patch_head_file = None
        patch_staged_file = None
        patch_stash_file = None
        patch_unversioned_base = None
        patch_unversioned_file = None
        rewind_to_hash = None
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

        # remote_name
        try:
            remote_name = self.params["remote_name"]
        except KeyError:
            pass # optional

        # branch_name
        try:
            branch_name = self.params["branch_name"]
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

        # port_staged
        try:
            port_staged = self.params["port_staged"]
            port_staged = True
        except KeyError:
            pass # optional

        # port_stash_count
        try:
            port_stash_count = self.params["port_stash_count"]
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

        # reset_staged
        try:
            reset_staged = self.params["reset_staged"]
            reset_staged = True
        except KeyError:
            pass # optional

        # reset_stash_count
        try:
            reset_stash_count = self.params["reset_stash_count"]
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

        # patch_staged_file
        try:
            patch_staged_file = self.params["patch_staged_file"]
        except KeyError:
            pass # optional

        # patch_stash_file
        try:
            patch_stash_file = self.params["patch_stash_file"]
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

        # rewind_to_hash
        try:
            rewind_to_hash = self.params["rewind_to_hash"]
        except KeyError:
            pass # optional

        # rewind_like_source
        try:
            rewind_like_source = self.params["rewind_like_source"]
            rewind_like_source = True
        except KeyError:
            pass # optional

        return True, (target_path, operation, source_url, remote_name, branch_name, source_path, default_filter, filter_include, filter_exclude, port_head, port_staged, port_stash_count, port_unversioned, port_previous_count, port_cherry_pick_previous, reset_head, reset_staged, reset_stash_count, reset_unversioned, reset_previous_count, patch_head_file, patch_staged_file, patch_stash_file, patch_unversioned_base, patch_unversioned_file, rewind_to_hash, rewind_like_source)

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        target_path, operation, source_url, remote_name, branch_name, source_path, default_filter, filter_include, filter_exclude, port_head, port_staged, port_stash_count, port_unversioned, port_previous_count, port_cherry_pick_previous, reset_head, reset_staged, reset_stash_count, reset_unversioned, reset_previous_count, patch_head_files, patch_staged_files, patch_stash_files, patch_unversioned_base, patch_unversioned_files, rewind_to_hash, rewind_like_source = r

        # delegate
        if operation == "clone_repo":
            return self.task_clone_repo(feedback_object, source_url, target_path, remote_name)
        elif operation == "pull_repo":
            return self.task_pull_repo(feedback_object, target_path, remote_name, branch_name)
        elif operation == "port_repo":
            return self.task_port_repo(feedback_object, source_path, target_path, default_filter, filter_include, filter_exclude, port_head, port_staged, port_stash_count, port_unversioned, port_previous_count, port_cherry_pick_previous)
        elif operation == "reset_repo":
            return self.task_reset_repo(feedback_object, target_path, default_filter, filter_include, filter_exclude, reset_head, reset_staged, reset_stash_count, reset_unversioned, reset_previous_count)
        elif operation == "rewind_repo":
            return self.task_rewind_repo(feedback_object, target_path, source_path, rewind_to_hash, rewind_like_source)
        elif operation == "patch_repo":
            return self.task_patch_repo(feedback_object, target_path, patch_head_files, patch_staged_files, patch_stash_files, patch_unversioned_base, patch_unversioned_files)
        else:
            return False, "Operation [%s] is invalid" % operation

    def task_clone_repo(self, feedback_object, source_url, target_path, remote_name):

        warnings = None

        if source_url is None:
            return False, "Source URL is required for task_clone_repo"

        if os.path.exists(target_path):
            return False, "Target path [%s] already exists" % target_path

        v, r = git_lib.clone_ext(source_url, target_path, remote_name)
        if not v:
            return False, r
        proc_result = r[0]
        proc_stdout = r[1]
        proc_stderr = r[2]

        # autobackup outputs
        output_list = [("git_plugin_stdout", proc_stdout, "Git's stdout"), ("git_plugin_stderr", proc_stderr, "Git's stderr")]
        warnings = log_helper.add_to_warnings(warnings, output_backup_helper.dump_outputs_autobackup(proc_result, feedback_object, output_list))

        if not proc_result:
            return False, proc_stderr

        return True, warnings

    def task_pull_repo(self, feedback_object, target_path, remote_name, branch_name):

        if not os.path.exists(target_path):
            return False, "Target path [%s] does not exist" % target_path

        if remote_name is None and branch_name is None:

            v, r = git_lib.pull_default(target_path)
            if not v:
                return False, r

        else:

            if remote_name is None:
                return False, "Branch name was specified, but remote name was not"

            if branch_name is None:
                return False, "Remote name was specified, but branch name was not"

            v, r = git_lib.pull(target_path, remote_name, branch_name)
            if not v:
                return False, r

        return True, None

    def task_port_repo(self, feedback_object, source_path, target_path, default_filter, filter_include, filter_exclude, port_head, port_staged, port_stash_count, port_unversioned, port_previous_count, port_cherry_pick_previous):

        if source_path is None:
            return False, "Source path (source_path) is required for task_port_repo"
        if not os.path.exists(source_path):
            return False, "Source path [%s] does not exist" % source_path

        if not os.path.exists(target_path):
            return False, "Target path [%s] does not exist" % target_path

        if port_stash_count is None:
            port_stash_count = "0"
        if not port_stash_count.lstrip("-").isnumeric():
            return False, "Invalid stash_count - expected numeric string: [%s]" % port_stash_count

        if port_previous_count is None:
            port_previous_count = "0"
        if not port_previous_count.isnumeric():
            return False, "Invalid previous_count - expected numeric string: [%s]" % port_previous_count

        port_stash_count = int(port_stash_count)
        port_previous_count = int(port_previous_count)

        v, r = port_git_repo.port_git_repo(source_path, target_path, default_filter, filter_include, filter_exclude, port_head, port_staged, port_stash_count, port_unversioned, port_previous_count, port_cherry_pick_previous)
        if not v:
            return False, r

        return True, None

    def task_reset_repo(self, feedback_object, target_path, default_filter, filter_include, filter_exclude, reset_head, reset_staged, reset_stash_count, reset_unversioned, reset_previous_count):

        if not os.path.exists(target_path):
            return False, "Target path [%s] does not exist" % target_path

        if reset_stash_count is None:
            reset_stash_count = "0"
        if not reset_stash_count.lstrip("-").isnumeric():
            return False, "Invalid stash_count - expected numeric string: [%s]" % reset_stash_count

        if reset_previous_count is None:
            reset_previous_count = "0"
        if not reset_previous_count.isnumeric():
            return False, "Invalid previous_count - expected numeric string: [%s]" % reset_previous_count

        reset_stash_count = int(reset_stash_count)
        reset_previous_count = int(reset_previous_count)

        v, r = reset_git_repo.reset_git_repo(target_path, default_filter, filter_include, filter_exclude, reset_head, reset_staged, reset_stash_count, reset_unversioned, reset_previous_count)
        if not v:
            return False, r
        backed_up_patches = r

        for w in backed_up_patches:
            feedback_object(w)

        warning_msg = None
        if len(backed_up_patches) > 0:
            warning_msg = "reset_git_repo has produced output"

        return True, warning_msg

    def task_rewind_repo(self, feedback_object, target_path, source_path, rewind_to_hash, rewind_like_source):

        if not os.path.exists(target_path):
            return False, "Target path [%s] does not exist" % target_path

        if (rewind_to_hash is not None) and rewind_like_source:
            return False, "rewind_repo should receive either rewind_to_hash xor rewind_like_source - never both at the same time."

        if rewind_like_source:

            if source_path is None:
                return False, "Source path (source_path) is required for task_rewind_repo (when passed rewind_like_source)"
            if not os.path.exists(source_path):
                return False, "Source path [%s] does not exist" % source_path

            v, r = git_lib.get_head_hash(source_path)
            if not v:
                return False, "Unable to retrieve head hash of source path [%s]: [%s]" % (source_path, r)
            rewind_to_hash = r

        if rewind_to_hash is None:
            return False, "No hash to rewind to (target_path: [%s])" % target_path

        v, r = git_lib.get_previous_hash_list(target_path)
        if not v:
            return False, "Unable to retrieve previous hash list of target path [%s]: [%s]" % (target_path, r)
        prev_hashes = r

        c = 0
        found = False
        for phi in prev_hashes:

            local_rewind_to_hash = rewind_to_hash
            if len(local_rewind_to_hash) > len(phi):
                local_rewind_to_hash = local_rewind_to_hash[:len(phi)]

            if local_rewind_to_hash == phi:
                found = True
                break

            c += 1

        if not found:
            return False, "Failed attempting to rewind repo [%s]: Hash [%s] was not found" % (source_path, rewind_to_hash)

        v, r = reset_git_repo.reset_git_repo(target_path, "include", [], [], False, False, 0, False, c)
        if not v:
            return False, r
        backed_up_patches = r

        for w in backed_up_patches:
            feedback_object(w)

        warning_msg = None
        if len(backed_up_patches) > 0:
            warning_msg = "reset_git_repo has produced output"

        return True, warning_msg

    def task_patch_repo(self, feedback_object, target_path, patch_head_files, patch_staged_files, patch_stash_files, patch_unversioned_base, patch_unversioned_files):

        # apply_git_patch supports different unversioned_bases per unversioned_file
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

        if not isinstance(patch_staged_files, list) and patch_staged_files is not None:
            patch_staged_files = [patch_staged_files]
        elif patch_staged_files is None:
            patch_staged_files = []

        if not isinstance(patch_stash_files, list) and patch_stash_files is not None:
            patch_stash_files = [patch_stash_files]
        elif patch_stash_files is None:
            patch_stash_files = []

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

        v, r = apply_git_patch.apply_git_patch(target_path, patch_head_files, patch_staged_files, patch_stash_files, unversioned_patches)
        if not v:
            return False, r

        return True, None
