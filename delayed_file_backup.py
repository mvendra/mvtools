#!/usr/bin/env python3

import sys
import os

import path_utils
import mvtools_exception

class delayed_file_backup:
    def __init__(self, _storage_path):
        self.storage_path = _storage_path
        if os.path.exists(self.storage_path):
            raise mvtools_exception.mvtools_exception("Path [%s] already exists." % self.storage_path)

    def _ascertain_storage_folder(self, subpath):

        if not os.path.exists(self.storage_path):
            os.mkdir(self.storage_path)
        if subpath is None:
            return
        final_path = path_utils.concat_path(self.storage_path, subpath)
        if not path_utils.guaranteefolder(final_path):
            raise mvtools_exception.mvtools_exception("Unable to guarantee final path [%s]." % final_path)

    def make_backup(self, subpath, filename, contents):

        self._ascertain_storage_folder(subpath)

        final_base_path = self.storage_path
        if subpath is not None:
            final_base_path = path_utils.concat_path(final_base_path, subpath)

        target_file_full_path = path_utils.concat_path(final_base_path, filename)
        if os.path.exists(target_file_full_path):
            return False, target_file_full_path

        file_mode = "w"
        if isinstance(contents, bytes):
            file_mode = "wb"

        with open(target_file_full_path, file_mode) as f:
            f.write(contents)

        return True, target_file_full_path

    def make_backup_frompath(self, subpath, filename, source_full_filename):

        self._ascertain_storage_folder(subpath)

        final_base_path = self.storage_path
        if subpath is not None:
            final_base_path = path_utils.concat_path(final_base_path, subpath)

        target_file_full_path = path_utils.concat_path(final_base_path, filename)
        if os.path.exists(target_file_full_path):
            return False, target_file_full_path

        if not os.path.exists(source_full_filename) and not path_utils.is_path_broken_symlink(source_full_filename):
            return False, target_file_full_path

        if filename == path_utils.basename_filtered(source_full_filename):
            if not path_utils.copy_to(source_full_filename, path_utils.dirname_filtered(target_file_full_path)):
                return False, target_file_full_path
        else:
            if not path_utils.copy_to_and_rename(source_full_filename, path_utils.dirname_filtered(target_file_full_path), filename):
                return False, target_file_full_path

        return True, target_file_full_path

if __name__ == "__main__":
    print("Hello from %s" % path_utils.basename_filtered(__file__))
