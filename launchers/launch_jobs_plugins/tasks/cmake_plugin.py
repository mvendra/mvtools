#!/usr/bin/env python3

import os

import path_utils
import maketimestamp
import mvtools_envvars

import launch_jobs
import cmake_lib

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "cmake"

    def run_task(self, feedback_object, execution_name=None):

        cmake_path = None
        install_prefix = None
        source_path = None
        output_path = None
        gen_type = None
        toolchain = None
        build_type = None
        save_output = None
        suppress_cmake_output = False

        # cmake_path
        try:
            cmake_path = self.params["cmake_path"]
        except KeyError:
            pass # optional

        # install_prefix
        try:
            install_prefix = self.params["install_prefix"]
        except KeyError:
            pass # optional

        # source_path
        try:
            source_path = self.params["source_path"]
        except KeyError:
            return False, "cmake failed - source_path is a required parameter"

        # output_path
        try:
            output_path = self.params["output_path"]
        except KeyError:
            return False, "cmake failed - output_path is a required parameter"

        # gen_type
        try:
            gen_type = self.params["gen_type"]
        except KeyError:
            return False, "cmake failed - gen_type is a required parameter"

        # toolchain
        try:
            toolchain = self.params["toolchain"]
        except KeyError:
            pass # optional

        # build_type
        try:
            build_type = self.params["build_type"]
        except KeyError:
            pass # optional

        # save_output
        try:
            save_output = self.params["save_output"]
        except KeyError:
            pass # optional

        # suppress_cmake_output
        if "suppress_cmake_output" in self.params:
            suppress_cmake_output = True

        # custom options
        # sample usage (inside the dsltype20 file): {option: "COPY_WX_LIBS:STRING=1"}
        custom_options = []
        try:
            custom_options_read = self.params["option"]
            if isinstance(custom_options_read, list):
                custom_options = custom_options_read
            else:
                custom_options.append(custom_options_read)
        except KeyError:
            pass # optional

        # pre-validate parameters
        if not os.path.exists(source_path):
            return False, "cmake failed - source_path [%s] does not exist." % source_path
        if not os.path.exists(output_path):
            return False, "cmake failed - output_path [%s] does not exist." % output_path

        options = cmake_lib.boot_options()

        # toolchain
        if toolchain is not None:
            options = cmake_lib.set_option_toolchain(options, toolchain)

        # install_prefix
        if install_prefix is not None:
            options = cmake_lib.set_option_install_prefix(options, install_prefix)

        # build_type
        if build_type is not None:
            options = cmake_lib.set_option_build_type(options, build_type)

        # generic options
        for opt in custom_options:
            options = cmake_lib.set_option_parse(options, opt)

        # save_output
        if save_output is not None:
            if os.path.exists(save_output):
                return False, "cmake_plugin: save_output [%s] points to a preexisting path" % save_output

        v, r = cmake_lib.configure_and_generate(cmake_path, suppress_cmake_output, source_path, output_path, gen_type, options)
        if save_output is not None:
            with open(save_output, "w") as f:
                f.write(r)
            feedback_object("Cmake's output has been saved to: [%s]" % save_output)
        if not v:

            v2, r2 = mvtools_envvars.mvtools_envvar_read_temp_path()
            if not v2:
                return False, "cmake_plugin failed: [%s]" % r2

            ts_now = maketimestamp.get_timestamp_now_compact()
            cmake_output_dump_filename = path_utils.concat_path(r2, "cmake_plugin_output_backup_%s.txt" % ts_now)
            if os.path.exists(cmake_output_dump_filename):
                return False, "cmake_plugin failed - output dump file [%s] already exists" % cmake_output_dump_filename

            with open(cmake_output_dump_filename, "w") as f:
                f.write(r)
            feedback_object("cmake failed - output was saved to [%s]" % cmake_output_dump_filename)

        if r is not None and suppress_cmake_output:
            r = "cmake's output was suppressed"
        return v, r
