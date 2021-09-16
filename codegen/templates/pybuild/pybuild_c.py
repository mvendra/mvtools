#!/usr/bin/env python3

import sys
import os

import get_platform
import generic_run
import path_utils

"""
build.py
A Python template for building C17 programs

This script is supposed to be integrated similar to
the following structure:

(project)/
(project)/proj/                         (project files; codelite, codeblocks, visual studio, xcode, makefiles, etc)
(project)/proj/pybuild
(project)/proj/pybuild/build.py          (this script)

(project)/build/                        (intermediate/object files - by platform, arch and mode)
(project)/build/linux_x64_debug
(project)/build/linux_x64_release

(project)/run/                          (final files/runtime folder - by platform, arch and mode)
(project)/run/linux_x64_debug
(project)/run/linux_x64_release

(project)/src
(project)/lib
(project)/lib/third_party

... and so on.
"""

class Builder():

    def __init__(_self, basepath, options):

        _self.basepath = basepath
        _self.options = _self.parseoptions(options)

        _self.appname = "testapp"
        _self.compiler = "gcc"

        _self.src = ["main.c", "second.c"]

        _self.src_base = "../../src/"
        _self.obj_base = "../../build/"
        _self.run_base = "../../run/"

        _self.include = []
        _self.include.append("-I%s" % _self.src_base)

        _self.ldflags = []

        _self.plat = get_platform.getplat()
        _self.arch = get_platform.getarch()
        _self.mode = _self.options["mode"]

        _self.target = _self.plat + "_" + _self.arch + "_" + _self.mode

        _self.obj_full = _self.obj_base + _self.target
        _self.run_full = _self.run_base + _self.target

        _self.app_full_name = _self.run_full + "/" + _self.appname
        _self.all_objs = [path_utils.replace_extension(x, ".c", ".o") for x in _self.src]

        _self.cpp_flags_common = ["-Wall", "-Wextra", "-pedantic", "-Werror", "-fPIC", "-std=c17"] 
        _self.cpp_flags_debug = ["-g", "-D_GLIBCXX_DEBUG"]
        _self.cpp_flags_release = ["-O2"]

        _self.cpp_flags_use = _self.cpp_flags_common
        if _self.mode == "debug":
            _self.cpp_flags_use += _self.cpp_flags_debug
        elif _self.mode == "release":
            _self.cpp_flags_use += _self.cpp_flags_release

    def parseoptions(_self, options):

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

    def run(_self):

        if _self.options["target"] == "clean":
            _self.do_clean()
        elif _self.options["target"] == "compile":
            _self.do_compile()
        elif _self.options["target"] == "link":
            _self.do_link()
        elif _self.options["target"] == "rebuild":
            _self.do_rebuild()
        elif _self.options["target"] == "all":
            _self.do_all()

    def do_clean(_self):

        for o in _self.all_objs:
            cmd = ["rm"]
            full_obj = _self.obj_full + "/" + o
            cmd.append(full_obj)
            _self.call_cmd(cmd)

        cmd = ["rm", _self.app_full_name]
        _self.call_cmd(cmd)

    def do_compile(_self):

        for s in _self.src:
            cmd = [_self.compiler]
            if len(_self.include) > 0:
                for i in _self.include:
                    cmd.append(i)
            cmd += _self.cpp_flags_use
            cmd += ["-c", _self.src_base + s, "-o", _self.obj_full + "/" +  path_utils.replace_extension(s, ".c", ".o")]
            _self.call_cmd(cmd)

    def do_link(_self):

        cmd = [_self.compiler, "-o", _self.app_full_name]
        cmd += [_self.obj_full + "/" + x for x in _self.all_objs]

        if len(_self.ldflags) > 0:
            for l in _self.ldflags:
                cmd.append(_self.ldflags)

        _self.call_cmd(cmd)

    def do_rebuild(_self):
        _self.do_all()

    def do_all(_self):
        _self.do_clean()
        _self.do_compile()
        _self.do_link()

    def call_cmd(_self, cmd):

        cmd_str = ""
        for c in cmd:
            cmd_str += "%s " % c
        cmd_str = cmd_str.rstrip()

        v, r = generic_run.run_cmd_simple(cmd)
        if v:
            print("%s: Command succeeded." % cmd_str)
        else:
            print("%s: Failed: [%s]" % (cmd_str, r))

if __name__ == "__main__":

    opt = None
    if len(sys.argv) > 1:
        opt = sys.argv[1:]

    bd = Builder(os.path.abspath(path_utils.dirname_filtered(sys.argv[0])), opt)
    bd.run()
