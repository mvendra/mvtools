#!/usr/bin/env python3

import os

import launch_jobs
import path_utils
import sha256_wrapper
import sha512_wrapper

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "hash"

    def _read_params(self):

        operation = None
        target_archive = None
        hash_type = None
        target_hash = None
        target_hash_file = None

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

        # hash_type
        try:
            hash_type = self.params["hash_type"]
        except KeyError:
            return False, "hash_type is a required parameter"

        # target_hash
        try:
            target_hash = self.params["target_hash"]
        except KeyError:
            pass # optional

        # target_hash_file
        try:
            target_hash_file = self.params["target_hash_file"]
        except KeyError:
            pass # optional

        return True, (operation, target_archive, hash_type, target_hash, target_hash_file)

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        operation, target_archive, hash_type, target_hash, target_hash_file = r

        # delegate
        if operation == "extract_hash": # to file (only)
            return self.task_extract_hash(feedback_object, target_archive, hash_type, target_hash_file)
        elif operation == "check_hash_from_content":
            return self.task_check_hash_from_content(feedback_object, target_archive, hash_type, target_hash)
        elif operation == "check_hash_from_file":
            return self.task_check_hash_from_file(feedback_object, target_archive, hash_type, target_hash_file)
        else:
            return False, "Operation [%s] is invalid" % operation

    def task_extract_hash(self, feedback_object, target_archive, hash_type, target_hash_file):

        if target_archive is None:
            return False, "Target archive is required for task_extract_hash"

        if not os.path.exists(target_archive):
            return False, "Target archive does not [%s] exist" % target_archive

        if hash_type is None:
            return False, "Hash type is required for task_extract_hash"

        if hash_type != "sha256" and hash_type != "sha512":
            return False, "Hash type [%s] is unknown" % hash_type

        if target_hash_file is None:
            return False, "Target hash file is required for task_extract_hash"

        if os.path.exists(target_hash_file):
            return False, "Target hash file [%s] already exists" % target_hash_file

        hash_func = None
        if hash_type == "sha256":
            hash_func = sha256_wrapper.hash_sha_256_app_file
        elif hash_type == "sha512":
            hash_func = sha512_wrapper.hash_sha_512_app_file
        else:
            return False, "task_extract_hash not_reached"

        v, r = hash_func(target_archive)
        if not v:
            return False, r
        generated_hash = r

        with open(target_hash_file, "w") as f:
            f.write(generated_hash)

        return True, None

    def task_check_hash_from_content(self, feedback_object, target_archive, hash_type, target_hash):

        if target_archive is None:
            return False, "Target archive is required for task_check_hash_from_content"

        if not os.path.exists(target_archive):
            return False, "Target archive does not [%s] exist" % target_archive

        if hash_type is None:
            return False, "Hash type is required for task_check_hash_from_content"

        if hash_type != "sha256" and hash_type != "sha512":
            return False, "Hash type [%s] is unknown" % hash_type

        if target_hash is None:
            return False, "Target hash is required for task_check_hash_from_content"

        hash_func = None
        if hash_type == "sha256":
            hash_func = sha256_wrapper.hash_sha_256_app_file
        elif hash_type == "sha512":
            hash_func = sha512_wrapper.hash_sha_512_app_file
        else:
            return False, "task_check_hash_from_content not_reached"

        v, r = hash_func(target_archive)
        if not v:
            return False, r
        generated_hash = r

        if target_hash != generated_hash:
            return False, "Target hash [%s] does not match with generated hash [%s]" % (target_hash, generated_hash)

        return True, None

    def task_check_hash_from_file(self, feedback_object, target_archive, hash_type, target_hash_file):

        if target_archive is None:
            return False, "Target archive is required for task_check_hash_from_file"

        if not os.path.exists(target_archive):
            return False, "Target archive does not [%s] exist" % target_archive

        if hash_type is None:
            return False, "Hash type is required for task_check_hash_from_file"

        if hash_type != "sha256" and hash_type != "sha512":
            return False, "Hash type [%s] is unknown" % hash_type

        if target_hash_file is None:
            return False, "Target hash file is required for task_check_hash_from_file"

        if not os.path.exists(target_hash_file):
            return False, "Target hash file [%s] does not exist" % target_hash_file

        hash_func = None
        char_count_upper_bound = None
        if hash_type == "sha256":
            hash_func = sha256_wrapper.hash_sha_256_app_file
            char_count_upper_bound = 64
        elif hash_type == "sha512":
            hash_func = sha512_wrapper.hash_sha_512_app_file
            char_count_upper_bound = 128
        else:
            return False, "task_check_hash_from_file not_reached"

        v, r = hash_func(target_archive)
        if not v:
            return False, r
        generated_hash = r

        target_hash_file_read_contents = None
        with open(target_hash_file, "r") as f:
            target_hash_file_read_contents = f.read()
        target_hash_file_read_contents = target_hash_file_read_contents[:char_count_upper_bound]

        if target_hash_file_read_contents != generated_hash:
            return False, "Target's read hash [%s] does not match with generated hash [%s]" % (target_hash_file_read_contents, generated_hash)

        return True, None
