#!/usr/bin/env python3

import os

import launch_jobs
import cmake_lib

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "cmake"

    def run_task(self, feedback_object, execution_name=None):

        # cmake_path
        cmake_path = None
        try:
            cmake_path = self.params["cmake_path"]
        except KeyError:
            pass # optional

        # install_prefix
        install_prefix = None
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
        toolchain = None
        try:
            toolchain = self.params["toolchain"]
        except KeyError:
            pass # optional

        # suppress_cmake_output
        suppress_cmake_output = False
        if "suppress_cmake_output" in self.params:
            suppress_cmake_output = True

        # custom options
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

        # generic options
        for opt in custom_options:
            options = cmake_lib.set_option_parse(options, opt)

        v, r = cmake_lib.configure_and_generate(cmake_path, source_path, output_path, gen_type, options)
        if r is not None and suppress_cmake_output:
            r = "cmake's output was suppressed"
        return v, r
