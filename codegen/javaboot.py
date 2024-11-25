#!/usr/bin/env python3

import sys
import os
import stat

import path_utils

def default_java_app():

    local_contents = ""

    local_contents += "\npackage pak;\n\n"
    local_contents += "public class Main {\n\n"
    local_contents += "    public static void main(String[] args){\n"
    local_contents += "        System.out.println(\"test for echo\");\n"
    local_contents += "    }\n\n"
    local_contents += "}\n"

    return local_contents

if __name__ == "__main__":

    filename = "Main.java"
    target_base_path = os.getcwd()

    if len(sys.argv) > 1:
        filename = sys.argv[1]

    full_filename = path_utils.concat_path(target_base_path, filename)

    if os.path.exists(full_filename):
        print("File [%s] already exists" % full_filename)
        sys.exit(1)

    contents = default_java_app()
    with open(full_filename, "w") as f:
        f.write(contents)

    os.chmod(full_filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
