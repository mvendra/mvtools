#!/usr/bin/env python3

import sys
import os

import path_utils
import prjboot_util

import standard_c
import standard_cpp

def mkfile_c_contents(project_name):

    r  = ""

    # TARGETS
    r += ".PHONY : all prepfolders clean compile link\n"
    r += "\n"

    # PLUMBING
    r += "# PLUMBING\n"
    r += "COMPILER=gcc\n"
    r += "\n"

    # PROJECT SETUP
    r += "# PROJECT SETUP\n"
    r += "OUTNAME=%s\n" % project_name
    r += "SRC=main.c subfolder/second.c\n"
    r += "BASE=../../..\n"
    r += "BASE_DEP=$(BASE)/dep\n"
    r += "CFLAGS=\n"
    r += "INCLUDES=\n"
    r += "LDFLAGS=\n"
    r += "DEPS=\n"
    r += "POSTBUILD=\n"
    r += "\n"

    # AUTOCONF PREP
    r += "# AUTOCONF PREP\n"
    r += "BASE_SRC=$(BASE)/src\n"
    r += "BASE_TMP=$(BASE)/tmp\n"
    r += "BASE_OUT=$(BASE)/out\n"
    r += "\n"

    # DEFAULTS
    r += "# DEFAULTS\n"
    r += "PLAT=linux\n"
    r += "MODE=release\n"
    r += "\n"

    # MODE
    r += "# MODE\n"
    r += "ifeq ($(MODE),)\n"
    r += "\t# to use, do 'make MODE=debug'\n"
    r += "\tMODE=debug\n"
    r += "endif\n"
    r += "\n"

    # PLAT
    r += "# PLAT FLAGS\n"
    r += "UNAME_S := $(shell uname -s)\n"
    r += "\n"

    # LINUX
    r += "# LINUX\n"
    r += "ifeq ($(UNAME_S),Linux)\n"
    r += "\tPLAT=linux\n"
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("CFLAGS", "+=", standard_c.get_c_compiler_flags_linux_gcc())), "\n")
    r += "endif\n"
    r += "\n"

    # WINDOWS
    r += "# WINDOWS\n"
    r += "ifneq (,$(findstring CYGWIN,$(UNAME_S)))\n"
    r += "\tPLAT=windows\n"
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("CFLAGS", "+=", standard_c.get_c_compiler_flags_windows_gcc())), "\n")
    r += "endif\n"
    r += "\n"

    # MACOSX
    r += "# MACOSX\n"
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

    # ARCH FLAGS
    r += "# ARCH FLAGS\n"
    r += "CFLAGS+=-m64\n"
    r += "\n"

    # AUTOCONF COMPLETE
    r += "# AUTOCONF COMPLETE\n"
    r += "PLAT_MODE=$(PLAT)_$(MODE)\n"
    r += "BASE_TMP_FULL=$(BASE_TMP)/$(PLAT_MODE)\n"
    r += "OUT_FULL=$(BASE_OUT)/$(PLAT_MODE)\n"
    r += "ALL_OBJS=$(foreach src,$(SRC),$(BASE_TMP_FULL)/$(if $(filter-out ./,$(dir $(src))),$(subst /,_,$(dir $(src))),)$(notdir $(src:.c=.o)))\n"
    r += "FULL_APP_NAME=$(OUT_FULL)/$(OUTNAME)\n"
    r += "INCLUDES+=-I$(BASE_SRC)\n"
    r += "\n"

    # ALL
    r += "all: prepfolders compile link\n"
    r += "\n"

    # PREPFOLDERS
    r += "prepfolders:\n"
    r += "\t@mkdir -p $(BASE_TMP_FULL)\n"
    r += "\t@mkdir -p $(OUT_FULL)\n"
    r += "\n"

    # COMPILE
    r += "compile:\n"
    r += "\t$(foreach src,$(SRC),$(COMPILER) $(INCLUDES) $(CFLAGS) -c $(BASE_SRC)/$(src) -o $(BASE_TMP_FULL)/$(if $(filter-out ./,$(dir $(src))),$(subst /,_,$(dir $(src))),)$(notdir $(src:.c=.o));)\n"
    r += "\n"

    # LINK
    r += "link:\n"
    r += "\t$(COMPILER) -o $(FULL_APP_NAME) $(ALL_OBJS) $(LDFLAGS) $(DEPS)\n"
    r += "\t$(POSTBUILD)\n"
    r += "\n"

    # CLEAN
    r += "clean:\n"
    r += "\t$(foreach objs,$(ALL_OBJS),rm $(objs);)\n"
    r += "\trm $(FULL_APP_NAME)\n"

    ba_r = bytearray()
    ba_r.extend(map(ord, r))
    return ba_r

def generate_makefile_c(target_dir, project_name):

    # base folders / base structure
    prj_fullname_base = path_utils.concat_path(target_dir, project_name)
    base_build = path_utils.concat_path(prj_fullname_base, "build")
    base_src = path_utils.concat_path(prj_fullname_base, "src")

    # generate the actual C Makefile
    base_build_makefile_c = path_utils.concat_path(base_build, "makefile_c")
    prjboot_util.makedir_if_needed(base_build_makefile_c)
    base_build_makefile_fn = path_utils.concat_path(base_build_makefile_c, "Makefile")
    if not prjboot_util.writecontents(base_build_makefile_fn, mkfile_c_contents(project_name)):
        return False, "Failed creating [%s]" % base_build_makefile_fn

    # gitignore
    gitignore_filename = path_utils.concat_path(prj_fullname_base, ".gitignore")

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

    return True, None

def mkfile_cpp_contents(project_name):

    r  = ""

    # TARGETS
    r += ".PHONY : all prepfolders clean compile link\n"
    r += "\n"

    # PLUMBING
    r += "# PLUMBING\n"
    r += "COMPILER=g++\n"
    r += "\n"

    # PROJECT SETUP
    r += "# PROJECT SETUP\n"
    r += "OUTNAME=%s\n" % project_name
    r += "SRC=main.cpp subfolder/second.cpp\n"
    r += "BASE=../../..\n"
    r += "BASE_DEP=$(BASE)/dep\n"
    r += "CPPFLAGS=\n"
    r += "INCLUDES=\n"
    r += "LDFLAGS=\n"
    r += "DEPS=\n"
    r += "POSTBUILD=\n"
    r += "\n"

    # AUTOCONF PREP
    r += "# AUTOCONF PREP\n"
    r += "BASE_SRC=$(BASE)/src\n"
    r += "BASE_TMP=$(BASE)/tmp\n"
    r += "BASE_OUT=$(BASE)/out\n"
    r += "\n"

    # DEFAULTS
    r += "# DEFAULTS\n"
    r += "PLAT=linux\n"
    r += "MODE=release\n"
    r += "\n"

    # MODE
    r += "# MODE\n"
    r += "ifeq ($(MODE),)\n"
    r += "\t# to use, do 'make MODE=debug'\n"
    r += "\tMODE=debug\n"
    r += "endif\n"
    r += "\n"

    # PLAT
    r += "# PLAT FLAGS\n"
    r += "UNAME_S := $(shell uname -s)\n"
    r += "\n"

    # LINUX
    r += "# LINUX\n"
    r += "ifeq ($(UNAME_S),Linux)\n"
    r += "\tPLAT=linux\n"
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("CPPFLAGS", "+=", standard_cpp.get_cpp_compiler_flags_linux_gcc())), "\n")
    r += "endif\n"
    r += "\n"

    # WINDOWS
    r += "# WINDOWS\n"
    r += "ifneq (,$(findstring CYGWIN,$(UNAME_S)))\n"
    r += "\tPLAT=windows\n"
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("CPPFLAGS", "+=", standard_cpp.get_cpp_compiler_flags_windows_gcc())), "\n")
    r += "endif\n"
    r += "\n"

    # MACOSX
    r += "# MACOSX\n"
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

    # ARCH FLAGS
    r += "# ARCH FLAGS\n"
    r += "CFLAGS+=-m64\n"
    r += "\n"

    # AUTOCONF COMPLETE
    r += "# AUTOCONF COMPLETE\n"
    r += "PLAT_MODE=$(PLAT)_$(MODE)\n"
    r += "BASE_TMP_FULL=$(BASE_TMP)/$(PLAT_MODE)\n"
    r += "OUT_FULL=$(BASE_OUT)/$(PLAT_MODE)\n"
    r += "ALL_OBJS=$(foreach src,$(SRC),$(BASE_TMP_FULL)/$(if $(filter-out ./,$(dir $(src))),$(subst /,_,$(dir $(src))),)$(notdir $(src:.cpp=.o)))\n"
    r += "FULL_APP_NAME=$(OUT_FULL)/$(OUTNAME)\n"
    r += "INCLUDES+=-I$(BASE_SRC)\n"
    r += "\n"

    # ALL
    r += "all: prepfolders compile link\n"
    r += "\n"

    # PREPFOLDERS
    r += "prepfolders:\n"
    r += "\t@mkdir -p $(BASE_TMP_FULL)\n"
    r += "\t@mkdir -p $(OUT_FULL)\n"
    r += "\n"

    # COMPILE
    r += "compile:\n"
    r += "\t$(foreach src,$(SRC),$(COMPILER) $(INCLUDES) $(CPPFLAGS) -c $(BASE_SRC)/$(src) -o $(BASE_TMP_FULL)/$(if $(filter-out ./,$(dir $(src))),$(subst /,_,$(dir $(src))),)$(notdir $(src:.cpp=.o));)\n"
    r += "\n"

    # LINK
    r += "link:\n"
    r += "\t$(COMPILER) -o $(FULL_APP_NAME) $(ALL_OBJS) $(LDFLAGS) $(DEPS)\n"
    r += "\t$(POSTBUILD)\n"
    r += "\n"

    # CLEAN
    r += "clean:\n"
    r += "\t$(foreach objs,$(ALL_OBJS),rm $(objs);)\n"
    r += "\trm $(FULL_APP_NAME)\n"

    ba_r = bytearray()
    ba_r.extend(map(ord, r))
    return ba_r

def generate_makefile_cpp(target_dir, project_name):

    # base folders / base structure
    prj_fullname_base = path_utils.concat_path(target_dir, project_name)
    base_build = path_utils.concat_path(prj_fullname_base, "build")
    base_src = path_utils.concat_path(prj_fullname_base, "src")

    # generate the actual C++ Makefile
    base_build_makefile_cpp = path_utils.concat_path(base_build, "makefile_cpp")
    prjboot_util.makedir_if_needed(base_build_makefile_cpp)
    base_build_makefile_fn = path_utils.concat_path(base_build_makefile_cpp, "Makefile")
    if not prjboot_util.writecontents(base_build_makefile_fn, mkfile_cpp_contents(project_name)):
        return False, "Failed creating [%s]" % base_build_makefile_fn

    # gitignore
    gitignore_filename = path_utils.concat_path(prj_fullname_base, ".gitignore")

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

    return True, None
