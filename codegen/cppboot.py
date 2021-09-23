#!/usr/bin/env python3

import sys
import os

import path_utils
import standard_cpp

if __name__ == "__main__":

    filename = "main.cpp"
    target_base_path = os.getcwd()

    if len(sys.argv) > 1:
        filename = sys.argv[1]

    full_filename = path_utils.concat_path(target_base_path, filename)

    if os.path.exists(full_filename):
        print("File [%s] already exists" % full_filename)
        sys.exit(1)

    contents = standard_cpp.get_main_cpp_app()
    with open(full_filename, "w") as f:
        f.write(contents)
