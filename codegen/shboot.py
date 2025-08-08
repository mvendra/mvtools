#!/usr/bin/env python3

import sys
import os
import stat

import path_utils

def default_sh_app():

    local_contents = ""

    local_contents += "#!/bin/bash\n\n"
    local_contents += "function puaq(){ # puaq stands for Print Usage And Quit\n"
    local_contents += "    echo \"Usage: `basename $0` param\"\n"
    local_contents += "    if [ \"$1\" = true ]; then\n"
    local_contents += "        exit 0\n"
    local_contents += "    else\n"
    local_contents += "        exit 1\n"
    local_contents += "    fi\n"
    local_contents += "}\n\n"
    local_contents += "if [ -z $1 ]; then\n"
    local_contents += "    puaq false\n"
    local_contents += "fi\n\n"
    local_contents += "# code goes here\n"

    return local_contents

if __name__ == "__main__":

    filename = "testforecho.sh"
    target_base_path = os.getcwd()

    if len(sys.argv) > 1:
        filename = sys.argv[1]

    full_filename = path_utils.concat_path(target_base_path, filename)

    if os.path.exists(full_filename):
        print("File [%s] already exists" % full_filename)
        sys.exit(1)

    contents = default_sh_app()
    with open(full_filename, "w") as f:
        f.write(contents)

    os.chmod(full_filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
