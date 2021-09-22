#!/usr/bin/env python3

import sys
import os

import path_utils
import prjboot_util

import standard_c
import standard_cpp

def mkfile_cpp_contents(project_name):

    r  = ""

    # BASE SETUP
    r += ".PHONY : all prepfolders clean compile link\n"
    r += "\n"
    r += "COMPILER=g++\n"
    r += "\n"
    r += "APPNAME=%s\n" % project_name
    r += "BASE=../..\n"
    r += "BASE_SRC=$(BASE)/src\n"
    r += "BASE_OBJ=$(BASE)/build\n"
    r += "RUN=$(BASE)/run\n"
    r += "\n"

    # VARS PRESET
    r += "ARCH := $(shell getconf LONG_BIT)\n"
    r += "PLAT=linux\n"
    r += "MODE=release\n"
    r += "INCLUDES=\n"
    r += "CPPFLAGS=\n"
    r += "LDFLAGS=\n"
    r += "POSTBUILD=\n"
    r += "\n"

    # SOURCES
    r += "# SOURCES\n"
    r += "SRC=main.cpp subfolder/second.cpp\n"
    r += "\n"

    # MODE
    r += "# MODE\n"
    r += "ifeq ($(MODE),)\n"
    r += "\t# to use, do 'make MODE=debug'\n"
    r += "\tMODE=debug\n"
    r += "endif\n"
    r += "\n"

    # ARCH FLAGS
    r += "# ARCH FLAGS\n"
    r += "ifeq ($(ARCH),64)\n"
    r += "\tCPPFLAGS+=-m64\n"
    r += "endif\n"
    r += "\n"

    # PLAT
    r += "# PLAT FLAGS\n"
    r += "UNAME_S := $(shell uname -s)\n"

    # LINUX
    r += "\n# LINUX\n"
    r += "ifeq ($(UNAME_S),Linux)\n"
    r += "\tPLAT=linux\n"
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("CPPFLAGS", "+=", standard_cpp.get_cpp_compiler_flags_linux_gcc())), "\n")
    r += "endif\n"

    # WINDOWS
    r += "\n# WINDOWS\n"
    r += "ifneq (,$(findstring NT-5.1,$(UNAME_S)))\n"
    r += "\tPLAT=windows\n"
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("CPPFLAGS", "+=", standard_cpp.get_cpp_compiler_flags_windows_gcc())), "\n")
    r += "endif\n"

    # MACOSX
    r += "\n# MACOSX\n"
    r += "ifeq ($(UNAME_S),Darwin)\n"
    r += "\tPLAT=macosx\n"
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("CPPFLAGS", "+=", standard_cpp.get_cpp_compiler_flags_macosx_gcc())), "\n")
    r += "endif\n"
    r += "\n"

    # DEBUG CONFIG
    r += "# DEBUG\n"
    r += "ifeq ($(MODE),debug)\n"
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("CPPFLAGS", "+=", standard_cpp.get_cpp_compiler_flags_debug_gcc())), "\n")
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("LDFLAGS", "+=", standard_cpp.get_cpp_linker_flags_debug_gcc())), "\n")
    r += "endif\n"
    r += "\n"

    # RELEASE CONFIG
    r += "# RELEASE\n"
    r += "ifeq ($(MODE),release)\n"
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("CPPFLAGS", "+=", standard_cpp.get_cpp_compiler_flags_release_gcc())), "\n")
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("LDFLAGS", "+=", standard_cpp.get_cpp_linker_flags_release_gcc())), "\n")
    r += "\tPOSTBUILD=strip $(FULL_APP_NAME)\n"
    r += "endif\n"
    r += "\n"

    # FINAL VARS
    r += "PLAT_ARCH_MODE=$(PLAT)_x$(ARCH)_$(MODE)\n"
    r += "BASE_OBJ_FULL=$(BASE_OBJ)/$(PLAT_ARCH_MODE)\n"
    r += "RUN_FULL=$(RUN)/$(PLAT_ARCH_MODE)\n"
    r += "ALL_OBJS=$(foreach src,$(SRC),$(BASE_OBJ_FULL)/$(notdir $(src:.cpp=.o)))\n"
    r += "FULL_APP_NAME=$(RUN_FULL)/$(APPNAME)\n"
    r += "INCLUDES=-I$(BASE_SRC)\n"
    r += "\n"

    # TARGETS
    r += "all: prepfolders compile link\n"
    r += "\n"

    # PREPFOLDERS
    r += "prepfolders:\n"
    r += "\t@mkdir -p $(BASE_OBJ_FULL)\n"
    r += "\t@mkdir -p $(RUN_FULL)\n"
    r += "\n"

    # COMPILE
    r += "compile:\n"
    r += "\t$(foreach src,$(SRC),$(COMPILER) $(INCLUDES) $(CPPFLAGS) -c $(BASE_SRC)/$(src) -o $(BASE_OBJ_FULL)/$(notdir $(src:.cpp=.o));)\n"
    r += "\n"

    # LINK
    r += "link:\n"
    r += "\t$(COMPILER) -o $(FULL_APP_NAME) $(ALL_OBJS) $(LDFLAGS)\n"
    r += "\t$(POSTBUILD)\n"
    r += "\n"

    # CLEAN
    r += "clean:\n"
    r += "\t$(foreach objs,$(ALL_OBJS),rm $(objs);)\n"
    r += "\trm $(FULL_APP_NAME)\n"

    ba_r = bytearray()
    ba_r.extend(map(ord, r))
    return ba_r

def mkfile_c_contents(project_name):

    r  = ""

    # BASE SETUP
    r += ".PHONY : all prepfolders clean compile link\n"
    r += "\n"
    r += "COMPILER=gcc\n"
    r += "\n"
    r += "APPNAME=%s\n" % project_name
    r += "BASE=../..\n"
    r += "BASE_SRC=$(BASE)/src\n"
    r += "BASE_OBJ=$(BASE)/build\n"
    r += "RUN=$(BASE)/run\n"
    r += "\n"

    # VARS PRESET
    r += "ARCH := $(shell getconf LONG_BIT)\n"
    r += "PLAT=linux\n"
    r += "MODE=release\n"
    r += "INCLUDES=\n"
    r += "CFLAGS=\n"
    r += "LDFLAGS=\n"
    r += "POSTBUILD=\n"
    r += "\n"

    # SOURCES
    r += "# SOURCES\n"
    r += "SRC=main.c subfolder/second.c\n"
    r += "\n"

    # MODE
    r += "# MODE\n"
    r += "ifeq ($(MODE),)\n"
    r += "\t# to use, do 'make MODE=debug'\n"
    r += "\tMODE=debug\n"
    r += "endif\n"
    r += "\n"

    # ARCH FLAGS
    r += "# ARCH FLAGS\n"
    r += "ifeq ($(ARCH),64)\n"
    r += "\tCFLAGS+=-m64\n"
    r += "endif\n"
    r += "\n"

    # PLAT
    r += "# PLAT FLAGS\n"
    r += "UNAME_S := $(shell uname -s)\n"

    # LINUX
    r += "\n# LINUX\n"
    r += "ifeq ($(UNAME_S),Linux)\n"
    r += "\tPLAT=linux\n"
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("CFLAGS", "+=", standard_c.get_c_compiler_flags_linux_gcc())), "\n")
    r += "endif\n"

    # WINDOWS
    r += "\n# WINDOWS\n"
    r += "ifneq (,$(findstring NT-5.1,$(UNAME_S)))\n"
    r += "\tPLAT=windows\n"
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("CFLAGS", "+=", standard_c.get_c_compiler_flags_windows_gcc())), "\n")
    r += "endif\n"

    # MACOSX
    r += "\n# MACOSX\n"
    r += "ifeq ($(UNAME_S),Darwin)\n"
    r += "\tPLAT=macosx\n"
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("CFLAGS", "+=", standard_c.get_c_compiler_flags_macosx_gcc())), "\n")
    r += "endif\n"
    r += "\n"

    # DEBUG CONFIG
    r += "# DEBUG\n"
    r += "ifeq ($(MODE),debug)\n"
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("CFLAGS", "+=", standard_c.get_c_compiler_flags_debug_gcc())), "\n")
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("LDFLAGS", "+=", standard_c.get_c_linker_flags_debug_gcc())), "\n")
    r += "endif\n"
    r += "\n"

    # RELEASE CONFIG
    r += "# RELEASE\n"
    r += "ifeq ($(MODE),release)\n"
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("CFLAGS", "+=", standard_c.get_c_compiler_flags_release_gcc())), "\n")
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("LDFLAGS", "+=", standard_c.get_c_linker_flags_release_gcc())), "\n")
    r += "\tPOSTBUILD=strip $(FULL_APP_NAME)\n"
    r += "endif\n"
    r += "\n"

    # FINAL VARS
    r += "PLAT_ARCH_MODE=$(PLAT)_x$(ARCH)_$(MODE)\n"
    r += "BASE_OBJ_FULL=$(BASE_OBJ)/$(PLAT_ARCH_MODE)\n"
    r += "RUN_FULL=$(RUN)/$(PLAT_ARCH_MODE)\n"
    r += "ALL_OBJS=$(foreach src,$(SRC),$(BASE_OBJ_FULL)/$(notdir $(src:.c=.o)))\n"
    r += "FULL_APP_NAME=$(RUN_FULL)/$(APPNAME)\n"
    r += "INCLUDES=-I$(BASE_SRC)\n"
    r += "\n"

    # TARGETS
    r += "all: prepfolders compile link\n"
    r += "\n"

    # PREPFOLDERS
    r += "prepfolders:\n"
    r += "\t@mkdir -p $(BASE_OBJ_FULL)\n"
    r += "\t@mkdir -p $(RUN_FULL)\n"
    r += "\n"

    # COMPILE
    r += "compile:\n"
    r += "\t$(foreach src,$(SRC),$(COMPILER) $(INCLUDES) $(CFLAGS) -c $(BASE_SRC)/$(src) -o $(BASE_OBJ_FULL)/$(notdir $(src:.c=.o));)\n"
    r += "\n"

    # LINK
    r += "link:\n"
    r += "\t$(COMPILER) -o $(FULL_APP_NAME) $(ALL_OBJS) $(LDFLAGS)\n"
    r += "\t$(POSTBUILD)\n"
    r += "\n"

    # CLEAN
    r += "clean:\n"
    r += "\t$(foreach objs,$(ALL_OBJS),rm $(objs);)\n"
    r += "\trm $(FULL_APP_NAME)\n"

    ba_r = bytearray()
    ba_r.extend(map(ord, r))
    return ba_r

def generate_c_makefile(target_dir, project_name):

    # base folders / base structure
    prj_fullname_base = path_utils.concat_path(target_dir, project_name)
    base_prj = path_utils.concat_path(prj_fullname_base, "proj")

    base_build = path_utils.concat_path(prj_fullname_base, "build")
    base_build_linux_x64_debug = path_utils.concat_path(base_build, "linux_x64_debug")
    base_build_linux_x64_release = path_utils.concat_path(base_build, "linux_x64_release")
    base_build_windows_x64_debug = path_utils.concat_path(base_build, "windows_x64_debug")
    base_build_windows_x64_release = path_utils.concat_path(base_build, "windows_x64_release")
    base_build_macosx_x64_debug = path_utils.concat_path(base_build, "macosx_x64_debug")
    base_build_macosx_x64_release = path_utils.concat_path(base_build, "macosx_x64_release")

    base_run = path_utils.concat_path(prj_fullname_base, "run")
    base_run_linux_x64_debug = path_utils.concat_path(base_run, "linux_x64_debug")
    base_run_linux_x64_release = path_utils.concat_path(base_run, "linux_x64_release")
    base_run_windows_x64_debug = path_utils.concat_path(base_run, "windows_x64_debug")
    base_run_windows_x64_release = path_utils.concat_path(base_run, "windows_x64_release")
    base_run_macosx_x64_debug = path_utils.concat_path(base_run, "macosx_x64_debug")
    base_run_macosx_x64_release = path_utils.concat_path(base_run, "macosx_x64_release")

    base_src = path_utils.concat_path(prj_fullname_base, "src")

    prjboot_util.makedir_if_needed(prj_fullname_base)
    prjboot_util.makedir_if_needed(base_prj)

    prjboot_util.makedir_if_needed(base_build)
    prjboot_util.makedir_if_needed(base_build_linux_x64_debug)
    prjboot_util.makedir_if_needed(base_build_linux_x64_release)
    prjboot_util.makedir_if_needed(base_build_windows_x64_debug)
    prjboot_util.makedir_if_needed(base_build_windows_x64_release)
    prjboot_util.makedir_if_needed(base_build_macosx_x64_debug)
    prjboot_util.makedir_if_needed(base_build_macosx_x64_release)

    prjboot_util.makedir_if_needed(base_run)
    prjboot_util.makedir_if_needed(base_run_linux_x64_debug)
    prjboot_util.makedir_if_needed(base_run_linux_x64_release)
    prjboot_util.makedir_if_needed(base_run_windows_x64_debug)
    prjboot_util.makedir_if_needed(base_run_windows_x64_release)
    prjboot_util.makedir_if_needed(base_run_macosx_x64_debug)
    prjboot_util.makedir_if_needed(base_run_macosx_x64_release)

    prjboot_util.makedir_if_needed(base_src)

    # generate the actual C Makefile
    base_prj_makefile_c = path_utils.concat_path(base_prj, "makefile_c")
    prjboot_util.makedir_if_needed(base_prj_makefile_c)
    base_prj_makefile_fn = path_utils.concat_path(base_prj_makefile_c, "Makefile")
    if not prjboot_util.writecontents(base_prj_makefile_fn, mkfile_c_contents(project_name)):
        return False, "Failed creating [%s]" % base_prj_makefile_fn

    # main C file
    base_src_main_c_fn = path_utils.concat_path(base_src, "main.c")
    if not prjboot_util.writecontents(base_src_main_c_fn, standard_c.get_main_c_app()):
        return False, "Failed creating [%s]" % base_src_main_c_fn

    # secondary C file
    base_src_subfolder = path_utils.concat_path(base_src, "subfolder")
    prjboot_util.makedir_if_needed(base_src_subfolder)
    base_src_subfolder_secondary_c_fn = path_utils.concat_path(base_src_subfolder, "second.c")
    if not prjboot_util.writecontents(base_src_subfolder_secondary_c_fn, prjboot_util.secondary_c_app()):
        return False, "Failed creating [%s]" % base_src_subfolder_secondary_c_fn

    # gitignore
    gitignore_filename = path_utils.concat_path(prj_fullname_base, ".gitignore")
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "build/")
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "run/")

    return True, None

def generate_cpp_makefile(target_dir, project_name):

    # base folders / base structure
    prj_fullname_base = path_utils.concat_path(target_dir, project_name)
    base_prj = path_utils.concat_path(prj_fullname_base, "proj")

    base_build = path_utils.concat_path(prj_fullname_base, "build")
    base_build_linux_x64_debug = path_utils.concat_path(base_build, "linux_x64_debug")
    base_build_linux_x64_release = path_utils.concat_path(base_build, "linux_x64_release")
    base_build_windows_x64_debug = path_utils.concat_path(base_build, "windows_x64_debug")
    base_build_windows_x64_release = path_utils.concat_path(base_build, "windows_x64_release")
    base_build_macosx_x64_debug = path_utils.concat_path(base_build, "macosx_x64_debug")
    base_build_macosx_x64_release = path_utils.concat_path(base_build, "macosx_x64_release")

    base_run = path_utils.concat_path(prj_fullname_base, "run")
    base_run_linux_x64_debug = path_utils.concat_path(base_run, "linux_x64_debug")
    base_run_linux_x64_release = path_utils.concat_path(base_run, "linux_x64_release")
    base_run_windows_x64_debug = path_utils.concat_path(base_run, "windows_x64_debug")
    base_run_windows_x64_release = path_utils.concat_path(base_run, "windows_x64_release")
    base_run_macosx_x64_debug = path_utils.concat_path(base_run, "macosx_x64_debug")
    base_run_macosx_x64_release = path_utils.concat_path(base_run, "macosx_x64_release")

    base_src = path_utils.concat_path(prj_fullname_base, "src")

    prjboot_util.makedir_if_needed(prj_fullname_base)
    prjboot_util.makedir_if_needed(base_prj)

    prjboot_util.makedir_if_needed(base_build)
    prjboot_util.makedir_if_needed(base_build_linux_x64_debug)
    prjboot_util.makedir_if_needed(base_build_linux_x64_release)
    prjboot_util.makedir_if_needed(base_build_windows_x64_debug)
    prjboot_util.makedir_if_needed(base_build_windows_x64_release)
    prjboot_util.makedir_if_needed(base_build_macosx_x64_debug)
    prjboot_util.makedir_if_needed(base_build_macosx_x64_release)

    prjboot_util.makedir_if_needed(base_run)
    prjboot_util.makedir_if_needed(base_run_linux_x64_debug)
    prjboot_util.makedir_if_needed(base_run_linux_x64_release)
    prjboot_util.makedir_if_needed(base_run_windows_x64_debug)
    prjboot_util.makedir_if_needed(base_run_windows_x64_release)
    prjboot_util.makedir_if_needed(base_run_macosx_x64_debug)
    prjboot_util.makedir_if_needed(base_run_macosx_x64_release)

    prjboot_util.makedir_if_needed(base_src)

    # generate the actual C++ Makefile
    base_prj_makefile_cpp = path_utils.concat_path(base_prj, "makefile_cpp")
    prjboot_util.makedir_if_needed(base_prj_makefile_cpp)
    base_prj_makefile_fn = path_utils.concat_path(base_prj_makefile_cpp, "Makefile")
    if not prjboot_util.writecontents(base_prj_makefile_fn, mkfile_cpp_contents(project_name)):
        return False, "Failed creating [%s]" % base_prj_makefile_fn

    # main C++ file
    base_src_main_cpp_fn = path_utils.concat_path(base_src, "main.cpp")
    if not prjboot_util.writecontents(base_src_main_cpp_fn, standard_cpp.get_main_cpp_app()):
        return False, "Failed creating [%s]" % base_src_main_cpp_fn

    # secondary C++ file
    base_src_subfolder = path_utils.concat_path(base_src, "subfolder")
    prjboot_util.makedir_if_needed(base_src_subfolder)
    base_src_subfolder_secondary_cpp_fn = path_utils.concat_path(base_src_subfolder, "second.cpp")
    if not prjboot_util.writecontents(base_src_subfolder_secondary_cpp_fn, prjboot_util.secondary_c_app()):
        return False, "Failed creating [%s]" % base_src_subfolder_secondary_cpp_fn

    # gitignore
    gitignore_filename = path_utils.concat_path(prj_fullname_base, ".gitignore")
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "build/")
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "run/")

    return True, None
