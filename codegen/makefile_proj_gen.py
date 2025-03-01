#!/usr/bin/env python3

import sys
import os

import path_utils
import prjboot_util

import standard_c
import standard_cpp

def linux_mkfile_c_contents(project_name):

    r = ""

    # TARGETS
    r += ".PHONY : all prepfolders clean compile link\n"
    r += "\n"

    # PLUMBING
    r += "# PLUMBING\n"
    r += "COMPILER=gcc\n"
    r += "LINKER=$(COMPILER)\n"
    r += "\n"

    # AUTOCONF PREP
    r += "# AUTOCONF PREP\n"
    r += "BASE=../../..\n"
    r += "BASE_SRC=$(BASE)/src\n"
    r += "BASE_TMP=$(BASE)/tmp\n"
    r += "BASE_OUT=$(BASE)/out\n"
    r += "BASE_DEP=$(BASE)/dep\n"
    r += "\n"

    # PROJECT SETUP
    r += "# PROJECT SETUP\n"
    r += "OUTNAME=%s\n" % project_name
    r += "SRC=main.c subfolder/second.c\n"
    r += "INCLUDES=-I$(BASE_SRC)\n"
    r += "CFLAGS=%s\n" % prjboot_util.inline_opts(" ", standard_c.get_c_compiler_flags_linux_common_gcc())
    r += "LDFLAGS=%s\n" % prjboot_util.inline_opts(" ", standard_c.get_c_linker_flags_linux_common_gcc())
    r += "LIBS=%s\n" % prjboot_util.inline_opts(" ", standard_c.get_c_linker_libs_linux_common_gcc())
    r += "LIBS_AFTER_ASAN=\n"
    r += "POSTBUILD=\n"
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
    r += "endif\n"
    r += "\n"

    # MACOS
    r += "# MACOS\n"
    r += "ifeq ($(UNAME_S),Darwin)\n"
    r += "\tPLAT=macos\n"
    r += "endif\n"
    r += "\n"

    # DEBUG CONFIG
    r += "# DEBUG\n"
    r += "ifeq ($(MODE),debug)\n"
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("CFLAGS", "+=", standard_c.get_c_compiler_flags_linux_debug_gcc())), "\n")
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("LDFLAGS", "+=", standard_c.get_c_linker_flags_linux_debug_gcc())), "\n")
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("LIBS", "+=", standard_c.get_c_linker_libs_linux_debug_gcc())), "\n")
    r += "endif\n"
    r += "\n"

    # RELEASE CONFIG
    r += "# RELEASE\n"
    r += "ifeq ($(MODE),release)\n"
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("CFLAGS", "+=", standard_c.get_c_compiler_flags_linux_release_gcc())), "\n")
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("LDFLAGS", "+=", standard_c.get_c_linker_flags_linux_release_gcc())), "\n")
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("LIBS", "+=", standard_c.get_c_linker_libs_linux_release_gcc())), "\n")
    r += "\tPOSTBUILD=strip -g $(OUTNAME_FULL)\n"
    r += "endif\n"
    r += "\n"

    r += "# LIBS AFTER ASAN\n"
    r += "LIBS+=$(LIBS_AFTER_ASAN)\n"
    r += "\n"

    # AUTOCONF COMPLETE
    r += "# AUTOCONF COMPLETE\n"
    r += "TMP_FULL=$(BASE_TMP)/$(PLAT)/$(MODE)\n"
    r += "OUT_FULL=$(BASE_OUT)/$(PLAT)/$(MODE)\n"
    r += "ALL_OBJS=$(foreach src,$(SRC),$(TMP_FULL)/$(if $(filter-out ./,$(dir $(src))),$(subst /,_,$(dir $(src))),)$(notdir $(src:.c=.o)))\n"
    r += "OUTNAME_FULL=$(OUT_FULL)/$(OUTNAME)\n"
    r += "\n"

    # ALL
    r += "# TARGET: ALL\n"
    r += "all: prepfolders compile link\n"
    r += "\n"

    # PREPFOLDERS
    r += "# TARGET: PREPFOLDERS\n"
    r += "prepfolders:\n"
    r += "\t@mkdir -p $(TMP_FULL)\n"
    r += "\t@mkdir -p $(OUT_FULL)\n"
    r += "\n"

    # COMPILE
    r += "# TARGET: COMPILE\n"
    r += "compile:\n"
    r += "\t$(foreach src,$(SRC),$(COMPILER) $(INCLUDES) $(CFLAGS) -c $(BASE_SRC)/$(src) -o $(TMP_FULL)/$(if $(filter-out ./,$(dir $(src))),$(subst /,_,$(dir $(src))),)$(notdir $(src:.c=.o));)\n"
    r += "\n"

    # LINK
    r += "# TARGET: LINK\n"
    r += "link:\n"
    r += "\t$(LINKER) -o $(OUTNAME_FULL) $(ALL_OBJS) $(LDFLAGS) $(LIBS)\n"
    r += "\t$(POSTBUILD)\n"
    r += "\n"

    # CLEAN
    r += "# TARGET: CLEAN\n"
    r += "clean:\n"
    r += "\t$(foreach objs,$(ALL_OBJS),rm $(objs);)\n"
    r += "\trm $(OUTNAME_FULL)\n"

    ba_r = bytearray()
    ba_r.extend(map(ord, r))
    return ba_r

def generate_linux_makefile_c(target_dir, project_name):

    # base folders / base structure
    prj_fullname_base = path_utils.concat_path(target_dir, project_name)
    base_build = path_utils.concat_path(prj_fullname_base, "build")
    base_build_linux = path_utils.concat_path(base_build, "linux")
    base_src = path_utils.concat_path(prj_fullname_base, "src")

    # generate the actual C Makefile
    base_build_linux_makefile_c = path_utils.concat_path(base_build_linux, "makefile_c")
    prjboot_util.makedir_if_needed(base_build_linux_makefile_c)
    base_build_linux_makefile_c_fn = path_utils.concat_path(base_build_linux_makefile_c, "Makefile")
    if not prjboot_util.writecontents(base_build_linux_makefile_c_fn, linux_mkfile_c_contents(project_name)):
        return False, "Failed creating [%s]" % base_build_linux_makefile_c_fn

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

def linux_mkfile_cpp_contents(project_name):

    r = ""

    # TARGETS
    r += ".PHONY : all prepfolders clean compile link\n"
    r += "\n"

    # PLUMBING
    r += "# PLUMBING\n"
    r += "COMPILER=g++\n"
    r += "LINKER=$(COMPILER)\n"
    r += "\n"

    # AUTOCONF PREP
    r += "# AUTOCONF PREP\n"
    r += "BASE=../../..\n"
    r += "BASE_SRC=$(BASE)/src\n"
    r += "BASE_TMP=$(BASE)/tmp\n"
    r += "BASE_OUT=$(BASE)/out\n"
    r += "BASE_DEP=$(BASE)/dep\n"
    r += "\n"

    # PROJECT SETUP
    r += "# PROJECT SETUP\n"
    r += "OUTNAME=%s\n" % project_name
    r += "SRC=main.cpp subfolder/second.cpp\n"
    r += "INCLUDES=-I$(BASE_SRC)\n"
    r += "CPPFLAGS=%s\n" % prjboot_util.inline_opts(" ", standard_cpp.get_cpp_compiler_flags_linux_common_gcc())
    r += "LDFLAGS=%s\n" % prjboot_util.inline_opts(" ", standard_cpp.get_cpp_linker_flags_linux_common_gcc())
    r += "LIBS=%s\n" % prjboot_util.inline_opts(" ", standard_cpp.get_cpp_linker_libs_linux_common_gcc())
    r += "LIBS_AFTER_ASAN=\n"
    r += "POSTBUILD=\n"
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
    r += "endif\n"
    r += "\n"

    # MACOS
    r += "# MACOS\n"
    r += "ifeq ($(UNAME_S),Darwin)\n"
    r += "\tPLAT=macos\n"
    r += "endif\n"
    r += "\n"

    # DEBUG CONFIG
    r += "# DEBUG\n"
    r += "ifeq ($(MODE),debug)\n"
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("CPPFLAGS", "+=", standard_cpp.get_cpp_compiler_flags_linux_debug_gcc())), "\n")
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("LDFLAGS", "+=", standard_cpp.get_cpp_linker_flags_linux_debug_gcc())), "\n")
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("LIBS", "+=", standard_cpp.get_cpp_linker_libs_linux_debug_gcc())), "\n")
    r += "endif\n"
    r += "\n"

    # RELEASE CONFIG
    r += "# RELEASE\n"
    r += "ifeq ($(MODE),release)\n"
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("CPPFLAGS", "+=", standard_cpp.get_cpp_compiler_flags_linux_release_gcc())), "\n")
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("LDFLAGS", "+=", standard_cpp.get_cpp_linker_flags_linux_release_gcc())), "\n")
    r += prjboot_util.deco_if_not_empty("\t", (prjboot_util.unroll_var("LIBS", "+=", standard_cpp.get_cpp_linker_libs_linux_release_gcc())), "\n")
    r += "\tPOSTBUILD=strip -g $(OUTNAME_FULL)\n"
    r += "endif\n"
    r += "\n"

    r += "# LIBS AFTER ASAN\n"
    r += "LIBS+=$(LIBS_AFTER_ASAN)\n"
    r += "\n"

    # AUTOCONF COMPLETE
    r += "# AUTOCONF COMPLETE\n"
    r += "TMP_FULL=$(BASE_TMP)/$(PLAT)/$(MODE)\n"
    r += "OUT_FULL=$(BASE_OUT)/$(PLAT)/$(MODE)\n"
    r += "ALL_OBJS=$(foreach src,$(SRC),$(TMP_FULL)/$(if $(filter-out ./,$(dir $(src))),$(subst /,_,$(dir $(src))),)$(notdir $(src:.cpp=.o)))\n"
    r += "OUTNAME_FULL=$(OUT_FULL)/$(OUTNAME)\n"
    r += "\n"

    # ALL
    r += "# TARGET: ALL\n"
    r += "all: prepfolders compile link\n"
    r += "\n"

    # PREPFOLDERS
    r += "# TARGET: PREPFOLDERS\n"
    r += "prepfolders:\n"
    r += "\t@mkdir -p $(TMP_FULL)\n"
    r += "\t@mkdir -p $(OUT_FULL)\n"
    r += "\n"

    # COMPILE
    r += "# TARGET: COMPILE\n"
    r += "compile:\n"
    r += "\t$(foreach src,$(SRC),$(COMPILER) $(INCLUDES) $(CPPFLAGS) -c $(BASE_SRC)/$(src) -o $(TMP_FULL)/$(if $(filter-out ./,$(dir $(src))),$(subst /,_,$(dir $(src))),)$(notdir $(src:.cpp=.o));)\n"
    r += "\n"

    # LINK
    r += "# TARGET: LINK\n"
    r += "link:\n"
    r += "\t$(LINKER) -o $(OUTNAME_FULL) $(ALL_OBJS) $(LDFLAGS) $(LIBS)\n"
    r += "\t$(POSTBUILD)\n"
    r += "\n"

    # CLEAN
    r += "# TARGET: CLEAN\n"
    r += "clean:\n"
    r += "\t$(foreach objs,$(ALL_OBJS),rm $(objs);)\n"
    r += "\trm $(OUTNAME_FULL)\n"

    ba_r = bytearray()
    ba_r.extend(map(ord, r))
    return ba_r

def generate_linux_makefile_cpp(target_dir, project_name):

    # base folders / base structure
    prj_fullname_base = path_utils.concat_path(target_dir, project_name)
    base_build = path_utils.concat_path(prj_fullname_base, "build")
    base_build_linux = path_utils.concat_path(base_build, "linux")
    base_src = path_utils.concat_path(prj_fullname_base, "src")

    # generate the actual C++ Makefile
    base_build_linux_makefile_cpp = path_utils.concat_path(base_build_linux, "makefile_cpp")
    prjboot_util.makedir_if_needed(base_build_linux_makefile_cpp)
    base_build_linux_makefile_cpp_fn = path_utils.concat_path(base_build_linux_makefile_cpp, "Makefile")
    if not prjboot_util.writecontents(base_build_linux_makefile_cpp_fn, linux_mkfile_cpp_contents(project_name)):
        return False, "Failed creating [%s]" % base_build_linux_makefile_cpp_fn

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
