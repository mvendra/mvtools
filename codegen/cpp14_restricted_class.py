#!/usr/bin/env python3

import sys
import os

import path_utils

class cpp14_restricted_class:

    def __init__(__self, filename, header_prefix, namespaces, impl_ext = "cpp", header_ext = "h"):
        __self.filename = filename

        __self.impl_ext = impl_ext
        __self.header_ext = header_ext

        __self.header_prefix = header_prefix
        __self.namespaces = namespaces

        __self.INDENT_STEP = "    " # 4 spaces
        __self.indent = ""

    def writetofile(__self, thefile, contents):
        if os.path.exists(thefile):
            raise RuntimeError("%s already exists, so we are aborting." % thefile)
        with open(thefile, "w") as f:
            f.write(contents)

    def gen(__self):

        classname = __self.filename

        #############
        # HEADER FILE
        #############

        header_fname = __self.filename.lower() + "." + __self.header_ext
        if len(__self.header_prefix) > 0:
            guardian = "__%s_%s_H__" % (__self.header_prefix.upper(), classname.upper())
        else:
            guardian = "__%s_H__" % classname.upper()

        header = "\n#ifndef %s\n#define %s\n" % (guardian, guardian)

        # NAMESPACES BEGIN
        if len(__self.namespaces) > 0:
            header += __self.more("\n")
        for i in __self.namespaces:
            header += __self.more("namespace %s {\n" % i)
        header += __self.more("\n")

        # CLASS DECL
        header += __self.more("class %s final {\n\n" % classname)
        header += __self.more("public:\n\n")

        __self.inc_indent()

        # RULE OF 5
        header += __self.more("%s() = delete;\n" % classname)
        header += __self.more("~%s();\n\n" % classname)
        header += __self.more("%s(const %s&) = delete;\n" % (classname, classname))
        header += __self.more("%s(%s&&) = delete;\n" % (classname, classname))
        header += __self.more("%s& operator=(const %s&) = delete;\n" % (classname, classname))
        header += __self.more("%s& operator=(%s&&) = delete;\n\n" % (classname, classname))

        __self.dec_indent()

        header += __self.more("private:\n\n")

        header += __self.more("};\n")

        # NAMESPACES END
        if len(__self.namespaces) > 0:
            header += __self.more("\n")
        for i in reversed(__self.namespaces):
            header += __self.more("} // ns: %s\n" % i)
        header += __self.more("\n")

        header += __self.more("#endif // %s\n\n" % guardian)

        __self.writetofile(path_utils.concat_path(os.getcwd(), header_fname), header)

        ###########
        # IMPL FILE
        ###########

        impl_fname = __self.filename.lower() + "." + __self.impl_ext
        impl = "\n#include \"%s\"\n" % header_fname

        # NAMESPACES BEGIN
        if len(__self.namespaces) > 0:
            impl += __self.more("\n")
        for i in __self.namespaces:
            impl += __self.more("namespace %s {\n" % i)
        impl += __self.more("\n")

        #impl += __self.more("%s::%s(){\n}\n\n" % (classname, classname))
        impl += __self.more("%s::~%s(){\n}\n" % (classname, classname))

        # NAMESPACES END
        if len(__self.namespaces) > 0:
            impl += __self.more("\n")
        for i in reversed(__self.namespaces):
            impl += __self.more("} // ns: %s\n" % i)
        impl += __self.more("\n")

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

def puaq(): # print usage and quit
    print("Usage: %s filename [h=header_prefix] [n=namespace]*" % path_utils.basename_filtered(__file__)) 
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    filename = sys.argv[1]
    if '.' in filename:
        print("Please do not include the extension")
        sys.exit(1)

    header_prefix = ""
    namespaces = []

    if len(sys.argv) > 2:
        for i in sys.argv[2:]:
            if len(i) < 2:
                print("Invalid option: %s" % i)
                sys.exit(1) # invalid. these are optional parameters. we need the prefix to tell us what type it is

            if i[0] == "h":
                header_prefix = i[2:]

            if i[0] == "n":
                namespaces.append(i[2:])
    
    g = cpp14_restricted_class(filename, header_prefix, namespaces)
    try:
        g.gen()
    except Exception as msg:
        print(msg)

