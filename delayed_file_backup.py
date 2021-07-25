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
        subpath_split = path_utils.splitpath(subpath, "auto")
        merged_path = self.storage_path
        for sp in subpath_split:
            merged_path = path_utils.concat_path(merged_path, sp)
            if not os.path.exists(merged_path):
                os.mkdir(merged_path)

    def make_backup(self, subpath, filename, contents):
        self._ascertain_storage_folder(subpath)
        final_base_path = self.storage_path
        if subpath is not None:
            final_base_path = path_utils.concat_path(final_base_path, subpath)
        target_file_full_path = path_utils.concat_path(final_base_path, filename)
        if os.path.exists(target_file_full_path):
            return False, target_file_full_path
        with open(target_file_full_path, "w") as f:
            f.write(contents)
        return True, target_file_full_path

if __name__ == "__main__":
    print("Hello from %s" % os.path.basename(__file__))
