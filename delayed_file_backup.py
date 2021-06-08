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

    def _ascertain_storage_folder(self):
        if not os.path.exists(self.storage_path):
            os.mkdir(self.storage_path)

    def make_backup(self, filename, contents):
        self._ascertain_storage_folder()
        target_file_full_path = path_utils.concat_path(self.storage_path, filename)
        if os.path.exists(target_file_full_path):
            return False, target_file_full_path
        with open(target_file_full_path, "w") as f:
            f.write(contents)
        return True, target_file_full_path

if __name__ == "__main__":
    print("Hello from %s" % os.path.basename(__file__))
