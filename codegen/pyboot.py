#!/usr/bin/env python

import sys
import os
import stat

import path_utils

def default_py_app():

    local_contents = ""

    local_contents += "#!/usr/bin/env python\n\n"
    local_contents += "import sys\n"
    local_contents += "import os\n\n"
    local_contents += "import path_utils\n\n"
    local_contents += "def puaq(selfhelp):\n"
    local_contents += "    print(\"Usage: %s params\" % path_utils.basename_filtered(__file__))\n"
    local_contents += "    if selfhelp:\n"
    local_contents += "        sys.exit(0)\n"
    local_contents += "    else:\n"
    local_contents += "        sys.exit(1)\n\n"
    local_contents += "if __name__ == \"__main__\":\n\n"
    local_contents += "    if len(sys.argv) < 2:\n"
    local_contents += "        puaq(False)\n"
    local_contents += "    print(\"elo\")\n"

    return local_contents

if __name__ == "__main__":

    filename = "testforecho.py"
    target_base_path = os.getcwd()

    if len(sys.argv) > 1:
        filename = sys.argv[1]

    full_filename = path_utils.concat_path(target_base_path, filename)

    if os.path.exists(full_filename):
        print("File [%s] already exists" % full_filename)
        sys.exit(1)

    contents = default_py_app()
    with open(full_filename, "w") as f:
        f.write(contents)

    os.chmod(full_filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
