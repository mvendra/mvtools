#!/usr/bin/env python

import sys
import os
import stat

import path_utils

def default_html_page():

    local_contents = ""

    local_contents += "<html>\n"
    local_contents += "  <head>\n"
    local_contents += "    <title>\n"
    local_contents += "      Title\n"
    local_contents += "    </title>\n"
    local_contents += "  </head>\n"
    local_contents += "  <body>\n"
    local_contents += "    Test For Echo\n"
    local_contents += "  </body>\n"
    local_contents += "</html>"

    return local_contents

if __name__ == "__main__":

    filename = "index.html"
    target_base_path = os.getcwd()

    if len(sys.argv) > 1:
        filename = sys.argv[1]

    full_filename = path_utils.concat_path(target_base_path, filename)

    if os.path.exists(full_filename):
        print("File [%s] already exists" % full_filename)
        sys.exit(1)

    contents = default_html_page()
    with open(full_filename, "w") as f:
        f.write(contents)

    os.chmod(full_filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
