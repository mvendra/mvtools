#!/usr/bin/env python3

import sys
import os

import mvtools_exception
import terminal_colors
import get_platform
import generic_run
import path_utils
import standard_c

"""
build.py
A Python template for building C programs

This script is supposed to be integrated similar to
the following structure:

(project)/

(project)/build/
(project)/build/linux/
(project)/build/linux/pybuild_c/
(project)/build/linux/pybuild_c/pybuild_c.py

(project)/dep/
(project)/dep/linux/

(project)/tmp/
(project)/tmp/linux/
(project)/tmp/linux/debug/
(project)/tmp/linux/release/

(project)/out/
(project)/out/linux/
(project)/out/linux/debug/
(project)/out/linux/release/

(project)/src/
"""

def makedir_if_needed(path):
    if not os.path.exists(path):
        os.mkdir(path)
        return True
    return False

def unroll_path_dirname(path):

    local_path = ""

    dirname_subpath = path_utils.dirname_filtered(path)
    if dirname_subpath is None:
        return ""
    dirname_subpath_pieces = path_utils.splitpath(dirname_subpath, "no")

    for dsp in dirname_subpath_pieces:
        local_path += "%s_" % dsp

    return local_path

class Builder():

    def __init__(self, basepath, appname, sources, options):

        self.basepath = basepath
        self.options = self.parseoptions(options)
        self.compiler = "gcc"

        self.appname = appname
        self.src = sources

        self.src_base = "../../../src/"
        self.tmp_base = "../../../tmp/"
        self.out_base = "../../../out/"

        self.include = []
        self.include.append("-I%s" % self.src_base)

        self.plat = get_platform.getplat()
        self.mode = self.options["mode"]

        self.target = path_utils.concat_path(self.plat, self.mode)

        self.tmp_full = path_utils.concat_path(self.tmp_base, self.target)
        self.out_full = path_utils.concat_path(self.out_base, self.target)

        self.out_full_fn = path_utils.concat_path(self.out_full, self.appname)
        self.all_objs = [(unroll_path_dirname(x) + path_utils.replace_extension(path_utils.basename_filtered(x), ".c", ".o")) for x in self.src]

        # compiler / linker flags
        self.compiler_flags_common = []
        self.compiler_flags_debug = []
        self.compiler_flags_release = []
        self.linker_flags_common = []
        self.linker_flags_debug = []
        self.linker_flags_release = []

        # standard C hook - will add compiler / linker flags depending on the compiler, platform, mode, etc
        self.standard_c_hook()

        # select compiler flags to actually use
        self.compiler_flags_to_use = self.compiler_flags_common
        if self.mode == "debug":
            self.compiler_flags_to_use += self.compiler_flags_debug
        elif self.mode == "release":
            self.compiler_flags_to_use += self.compiler_flags_release

        # select linker flags to actually use
        self.linker_flags_to_use = self.linker_flags_common
        if self.mode == "debug":
            self.linker_flags_to_use += self.linker_flags_debug
        elif self.mode == "release":
            self.linker_flags_to_use += self.linker_flags_release

    def standard_c_hook(self):

        # common compiler flags
        if (self.plat == get_platform.PLAT_LINUX or self.plat == get_platform.PLAT_MACOSX) and self.compiler == "gcc":
            self.compiler_flags_common += standard_c.get_c_compiler_flags_linux_common_gcc()

        # debug compiler flags
        if self.mode == "debug" and self.compiler == "gcc":
            self.compiler_flags_debug += standard_c.get_c_compiler_flags_linux_debug_gcc()

        # release compiler flags
        if self.mode == "release" and self.compiler == "gcc":
            self.compiler_flags_release += standard_c.get_c_compiler_flags_linux_release_gcc()

        # common linker flags
        self.linker_flags_common += standard_c.get_c_linker_flags_linux_common_gcc()

        # debug linker flags
        if self.mode == "debug" and self.compiler == "gcc":
            self.linker_flags_debug += standard_c.get_c_linker_flags_linux_debug_gcc()

        # release linker flags
        if self.mode == "release" and self.compiler == "gcc":
            self.linker_flags_release += standard_c.get_c_linker_flags_linux_release_gcc()

    def parseoptions(self, options):

        opts = {}

        # fill in defaults
        opts["mode"] = "release"
        opts["target"] = "all"
        # other possible options: type (static, shared)

        if options is None:
            return opts

        if "release" in options:
            opts["mode"] = "release"
        if "debug" in options:
            opts["mode"] = "debug"

        if "clean" in options:
            opts["target"] = "clean"
        if "compile" in options:
            opts["target"] = "compile"
        if "link" in options:
            opts["target"] = "link"
        if "rebuild" in options:
            opts["target"] = "rebuild"
        if "all" in options:
            opts["target"] = "all"

        return opts

    def run(self):

        if self.options["target"] == "clean":
            self.do_clean()
        elif self.options["target"] == "compile":
            self.do_compile()
        elif self.options["target"] == "link":
            self.do_link()
        elif self.options["target"] == "rebuild":
            self.do_rebuild()
        elif self.options["target"] == "all":
            self.do_all()

    def do_structure(self):

        makedir_if_needed(self.tmp_base)
        makedir_if_needed(self.out_base)

        makedir_if_needed(self.tmp_full)
        makedir_if_needed(self.out_full)

    def do_clean(self):

        for o in self.all_objs:
            cmd = ["rm"]
            full_obj = self.tmp_full + "/" + o
            cmd.append(full_obj)
            self.call_cmd(cmd)

        cmd = ["rm", self.out_full_fn]
        self.call_cmd(cmd)

    def do_compile(self):

        for s in self.src:
            cmd = [self.compiler]
            if len(self.include) > 0:
                for i in self.include:
                    cmd.append(i)
            cmd += self.compiler_flags_to_use
            cmd += ["-c", self.src_base + s, "-o", self.tmp_full + "/" + unroll_path_dirname(s) + path_utils.replace_extension(path_utils.basename_filtered(s), ".c", ".o")]
            self.call_cmd(cmd)

    def do_link(self):

        cmd = [self.compiler, "-o", self.out_full_fn]
        cmd += [self.tmp_full + "/" + x for x in self.all_objs]

        if len(self.linker_flags_to_use) > 0:
            for l in self.linker_flags_to_use:
                cmd.append(l)

        self.call_cmd(cmd)

    def do_rebuild(self):
        self.do_clean()
        self.do_all()

    def do_all(self):
        self.do_structure()
        self.do_compile()
        self.do_link()

    def call_cmd(self, cmd):

        cmd_str = ""
        for c in cmd:
            cmd_str += "%s " % c
        cmd_str = cmd_str.rstrip()

        v, r = generic_run.run_cmd_simple(cmd)
        if not v:
            raise mvtools_exception.mvtools_exception("%s: Failed: [%s]" % (cmd_str, r.rstrip()))

        print("%s: Command succeeded." % cmd_str)

if __name__ == "__main__":

    appname = "testapp"
    src = ["main.c", "subfolder/second.c"]

    basepath = os.path.abspath(path_utils.dirname_filtered(sys.argv[0]))

    opt = None
    if len(sys.argv) > 1:
        opt = sys.argv[1:]

    bd = Builder(basepath, appname, src, opt)

    try:
        bd.run()
    except mvtools_exception.mvtools_exception as mvtex:
        print("%s%s%s" % (terminal_colors.TTY_RED, mvtex, terminal_colors.TTY_WHITE))
        sys.exit(1)

    print("%s%s%s" % (terminal_colors.TTY_GREEN, "All succeeded.", terminal_colors.TTY_WHITE))
