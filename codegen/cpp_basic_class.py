#!/usr/bin/env python3

import sys
import os

import path_utils

class cpp_basic_class:

    def __init__(__self, filename, impl_ext = "cpp", header_ext = "h"):
        __self.filename = filename

        __self.impl_ext = impl_ext
        __self.header_ext = header_ext

        __self.INDENT_STEP = "    " # 4 spaces
        __self.indent = ""

    def writetofile(__self, thefile, contents):
        if os.path.exists(thefile):
            raise RuntimeError("%s already exists, so we are aborting." % thefile)
        with open(thefile, "w") as f:
            f.write(contents)

    def gen(__self):

        classname = __self.filename.capitalize()

        # HEADER FILE

        header_fname = __self.filename + "." + __self.header_ext
        guardian = "__%s_H__" % classname.upper()

        header = "\n#ifndef %s\n#define %s\n\n" % (guardian, guardian)
        
        header += __self.more("class %s {\n\n" % classname)
        header += __self.more("public:\n\n")

        __self.inc_indent()

        header += __self.more("%s();\n" % classname)
        header += __self.more("~%s();\n\n" % classname)

        __self.dec_indent()

        header += __self.more("private:\n\n")

        header += __self.more("};\n\n")

        header += __self.more("#endif // %s\n\n" % guardian)

        __self.writetofile(path_utils.concat_path(os.getcwd(), header_fname), header)

        # IMPL FILE

        impl_fname = __self.filename + "." + __self.impl_ext
        impl = "\n#include \"%s\"\n\n" % header_fname

        impl += __self.more("%s::%s(){\n}\n\n" % (classname, classname))
        impl += __self.more("%s::~%s(){\n}\n\n" % (classname, classname))

        __self.writetofile(path_utils.concat_path(os.getcwd(), impl_fname), impl)

    def more(__self, content):
        return __self.indent + content
    def reset_indent(__self):
        __self.indent = ""
    def inc_indent(__self):
        __self.indent += __self.INDENT_STEP
    def dec_indent(__self):
        if __self.indent != "":
            __self.indent = __self.indent[:len(__self.indent)-len(__self.INDENT_STEP)]

def puaq(selfhelp): # print usage and quit
    print("Usage: %s filename" % path_utils.basename_filtered(__file__)) 
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq(False)

    filename = sys.argv[1]
    if "." in filename:
        print("Please do not include the extension")
        sys.exit(1)

    g = cpp_basic_class(filename)
    try:
        g.gen()
    except Exception as msg:
        print(msg)

