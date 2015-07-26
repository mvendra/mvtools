#!/usr/bin/env python

import sys
import os

class cpp_basic_class:

    def __init__(__self, filename):
        __self.filename = filename
        __self.INDENT_STEP = "  "
        __self.indent = ""

    def writetofile(__self, thefile, contents):
        with open(thefile, "w") as f:
            f.write(contents)

    def gen(__self):

        classname = __self.filename.capitalize()

        # HEADER FILE

        header_fname = __self.filename + ".h"
        guardian = "__%s_H__" % classname.upper()

        header = "\n#ifndef %s\n#define %s\n\n" % (guardian, guardian)
        
        header += __self.more("class %s {\n\n" % classname)
        __self.inc_indent()

        header += __self.more("public:\n\n")
        header += __self.more("%s();\n" % classname)
        header += __self.more("~%s();\n\n" % classname)

        header += __self.more("private:\n\n")

        __self.dec_indent()
        header += __self.more("};\n\n")

        header += __self.more("#endif // %s\n\n" % guardian)

        __self.writetofile(os.path.join(os.getcwd(), header_fname), header)

        # IMPL FILE

        impl_fname = __self.filename + ".cpp"
        impl = "\n#include \"%s\"\n\n" % header_fname

        impl += __self.more("%s::%s(){\n}\n\n" % (classname, classname))
        impl += __self.more("%s::~%s(){\n}\n\n" % (classname, classname))

        __self.writetofile(os.path.join(os.getcwd(), impl_fname), impl)

    def more(__self, content):
        return __self.indent + content
    def reset_indent(__self):
        __self.indent = ""
    def inc_indent(__self):
        __self.indent += __self.INDENT_STEP
    def dec_indent(__self):
        if __self.indent != "":
            __self.indent = __self.indent[:len(__self.indent)-len(__self.INDENT_STEP)]

def puaq(): # print usage and quit
    print("Usage: %s filename" % os.path.basename(__file__)) 
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    filename = sys.argv[1]
    if '.' in filename:
        print("Please do not include the extension")

    g = cpp_basic_class(filename)
    g.gen()

