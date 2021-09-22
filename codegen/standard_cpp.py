#!/usr/bin/env python3

import sys
import os

def get_main_cpp_app():

    contents = ""

    contents += "\n"
    contents += "#include <iostream>\n"
    contents += "\n"
    contents += "int main(int argc, char *argv[]){\n"
    contents += "\n"
    contents += "    (void)argc; (void)argv;\n"
    contents += "    std::cout << \"test for echo\" << std::endl;\n"
    contents += "\n"
    contents += "    return 0;\n"
    contents += "\n"
    contents += "}\n"
    contents += "\n"

    return contents

def get_cpp_compiler_flags_debug_gcc():

    contents = []

    contents.append("-g")
    contents.append("-Wall")
    contents.append("-Wextra")
    contents.append("-Werror")
    contents.append("-pedantic")
    contents.append("-Weffc++")
    contents.append("-fPIC")
    contents.append("-fsanitize=address")
    contents.append("-pthread")
    contents.append("-D_GLIBCXX_DEBUG")
    contents.append("-std=c++14")

    return contents

def get_cpp_compiler_flags_release_gcc():

    contents = []

    contents.append("-O2")
    contents.append("-Wall")
    contents.append("-Wextra")
    contents.append("-Werror")
    contents.append("-pedantic")
    contents.append("-fPIC")
    contents.append("-std=c++14")
    contents.append("-DNDEBUG")

    return contents

def get_cpp_compiler_flags_linux_gcc():

    contents = []

    return contents

def get_cpp_compiler_flags_windows_gcc():

    contents = []

    return contents

def get_cpp_compiler_flags_macosx_gcc():

    contents = []

    return contents

def get_cpp_linker_flags_debug_gcc():

    contents = []

    contents.append("-lasan")

    return contents

def get_cpp_linker_flags_release_gcc():

    contents = []

    return contents
