#!/usr/bin/env python3

import sys
import os

def get_main_c_app():

    contents = ""

    contents += "\n"
    contents += "#include <stdio.h>\n"
    contents += "\n"
    contents += "int main(int argc, char *argv[]){\n"
    contents += "\n"
    contents += "    (void)argc; (void)argv;\n"
    contents += "    printf(\"test for echo\\n\");\n"
    contents += "\n"
    contents += "    return 0;\n"
    contents += "\n"
    contents += "}\n"
    contents += "\n"

    return contents

def get_c_compiler_flags_debug_gcc():

    contents = []

    contents.append("-g")
    contents.append("-Wall")
    contents.append("-Wextra")
    contents.append("-Werror")
    contents.append("-pedantic")
    contents.append("-fPIC")
    contents.append("-fsanitize=address")
    contents.append("-D_GLIBCXX_DEBUG")

    return contents

def get_c_compiler_flags_release_gcc():

    contents = []

    contents.append("-O2")
    contents.append("-Wall")
    contents.append("-Wextra")
    contents.append("-Werror")
    contents.append("-pedantic")
    contents.append("-fPIC")
    contents.append("-DNDEBUG")

    return contents

def get_c_compiler_flags_linux_gcc():

    contents = []

    contents.append("-std=c17")

    return contents

def get_c_compiler_flags_windows_gcc():

    contents = []

    contents.append("-std=c17")

    return contents

def get_c_compiler_flags_macosx_gcc():

    contents = []

    contents.append("-std=c17")

    return contents

def get_c_linker_flags_debug_gcc():

    contents = []

    contents.append("-lasan")

    return contents

def get_c_linker_flags_release_gcc():

    contents = []

    return contents

def get_clang_version():

    contents = "14"

    return contents

def c_compiler_flags_debug_msvc():

    contents = []

    return contents

def c_compiler_flags_release_msvc():

    contents = []

    return contents

def c_compiler_flags_windows_msvc():

    contents = []

    contents.append("/std:c17")

    return contents
