#!/usr/bin/env python3

import sys
import os

def get_main_cpp_app():

    contents = ""

    contents += "\n"
    contents += "#include <cstdio>\n"
    contents += "\n"
    contents += "int main(int argc, char *argv[]){\n"
    contents += "\n"
    contents += "    (void)argc; (void)argv;\n"
    contents += "    std::printf(\"test for echo\\n\");\n"
    contents += "\n"
    contents += "    return 0;\n"
    contents += "\n"
    contents += "}\n"
    contents += "\n"

    return contents

def get_cpp_compiler_flags_linux_debug_gcc():

    contents = []

    contents.append("-g")
    contents.append("-Wall")
    contents.append("-Wextra")
    contents.append("-Werror")
    contents.append("-pedantic")
    contents.append("-Weffc++")
    contents.append("-fPIC")
    contents.append("-fsanitize=address")
    contents.append("-D_GLIBCXX_DEBUG")

    return contents

def get_cpp_compiler_flags_linux_release_gcc():

    contents = []

    contents.append("-O2")
    contents.append("-Wall")
    contents.append("-Wextra")
    contents.append("-Werror")
    contents.append("-pedantic")
    contents.append("-fPIC")
    contents.append("-DNDEBUG")

    return contents

def get_cpp_compiler_flags_linux_gcc():

    contents = []

    contents.append("-std=c++17")

    return contents

def get_cpp_compiler_flags_windows_gcc():

    contents = []

    contents.append("-std=c++17")

    return contents

def get_cpp_compiler_flags_macosx_gcc():

    contents = []

    contents.append("-std=c++17")

    return contents

def get_cpp_linker_flags_linux_debug_gcc():

    contents = []

    contents.append("-lasan")

    return contents

def get_cpp_linker_flags_linux_release_gcc():

    contents = []

    return contents

def get_clang_version():

    contents = "17"

    return contents

def get_cpp_compiler_flags_windows_debug_msvc():

    contents = []

    return contents

def get_cpp_compiler_flags_windows_release_msvc():

    contents = []

    return contents

def get_cpp_compiler_flags_windows_msvc():

    contents = []

    contents.append("/std:c++17")

    return contents
