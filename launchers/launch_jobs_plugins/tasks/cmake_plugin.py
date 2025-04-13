#!/usr/bin/env python3

import os

import path_utils
import log_helper
import output_backup_helper

import launch_jobs
import cmake_lib

def _assemble_options(build_type, install_prefix, toolchain, custom_options):

    options = cmake_lib.boot_options()

    # build_type
    if build_type is not None:
        options = cmake_lib.set_option_build_type(options, build_type)

    # install_prefix
    if install_prefix is not None:
        options = cmake_lib.set_option_install_prefix(options, install_prefix)

    # toolchain
    if toolchain is not None:
        options = cmake_lib.set_option_toolchain(options, toolchain)

    # generic options
    if custom_options is not None:
        for opt in custom_options:
            options = cmake_lib.set_option_parse(options, opt)

    return options

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "cmake"

    def _read_params(self):

        cmake_path = None
        output_path = None
        extract_options = None
        temp_path = None
        source_path = None
        gen_type = None
        build_type = None
        install_prefix = None
        toolchain = None
        custom_options = None
        save_output = None
        save_error_output = None
        suppress_stderr_warnings = None

        # cmake_path
        try:
            cmake_path = self.params["cmake_path"]
        except KeyError:
            pass # optional

        # output_path
        try:
            output_path = self.params["output_path"]
        except KeyError:
            return False, "output_path is a required parameter"

        # extract_options - special case (ie. hack)
        try:
            extract_options = self.params["extract_options"]
            if len(self.params) != 3 and len(self.params) != 4:
                return False, "extract_options requires three or four parameters" # mvtodo: coverage
            # temp_path
            try:
                temp_path = self.params["temp_path"]
            except KeyError:
                return False, "temp_path is a required parameter (for extract_options)"
            return True, (cmake_path, extract_options, temp_path, output_path)
        except KeyError:
            pass # optional

        # source_path
        try:
            source_path = self.params["source_path"]
        except KeyError:
            return False, "source_path is a required parameter"

        # gen_type
        try:
            gen_type = self.params["gen_type"]
        except KeyError:
            return False, "gen_type is a required parameter"

        # build_type
        try:
            build_type = self.params["build_type"]
        except KeyError:
            pass # optional

        # install_prefix
        try:
            install_prefix = self.params["install_prefix"]
        except KeyError:
            pass # optional

        # toolchain
        try:
            toolchain = self.params["toolchain"]
        except KeyError:
            pass # optional

        # custom_options
        # sample usage (inside the dsltype20 file): {option: "COPY_WX_LIBS:STRING=1"}
        try:
            custom_options_read = self.params["option"]
            if isinstance(custom_options_read, list):
                custom_options = custom_options_read
            else:
                custom_options = []
                custom_options.append(custom_options_read)
        except KeyError:
            pass # optional

        # save_output
        try:
            save_output = self.params["save_output"]
        except KeyError:
            pass # optional

        # save_error_output
        try:
            save_error_output = self.params["save_error_output"]
        except KeyError:
            pass # optional

        # suppress_stderr_warnings
        suppress_stderr_warnings = "suppress_stderr_warnings" in self.params

        # pre-validate parameters
        if not os.path.exists(source_path):
            return False, "source_path [%s] does not exist." % source_path
        if not os.path.exists(output_path):
            return False, "output_path [%s] does not exist." % output_path

        # save_output
        if save_output is not None:
            if os.path.exists(save_output):
                return False, "save_output [%s] points to a preexisting path" % save_output

        # save_error_output
        if save_error_output is not None:
            if os.path.exists(save_error_output):
                return False, "save_error_output [%s] points to a preexisting path" % save_error_output

        return True, (cmake_path, source_path, output_path, gen_type, build_type, install_prefix, toolchain, custom_options, save_output, save_error_output, suppress_stderr_warnings)

    def run_task(self, feedback_object, execution_name=None):

        warnings = None

        # read params
        v, r = self._read_params()
        if not v:
            return False, r

        # special case/hack - extract options and early-quit
        if len(r) == 4:
            cmake_path, extract_options, temp_path, output_path = r
            return cmake_lib.extract_options(cmake_path, extract_options, temp_path, output_path)

        cmake_path, source_path, output_path, gen_type, build_type, install_prefix, toolchain, custom_options, save_output, save_error_output, suppress_stderr_warnings = r

        # assemble options
        options = _assemble_options(build_type, install_prefix, toolchain, custom_options)

        # actual execution
        v, r = cmake_lib.configure_and_generate(cmake_path, source_path, output_path, gen_type, options)
        if not v:
            return False, r
        proc_result = r[0]
        proc_stdout = r[1]
        proc_stderr = r[2]

        # dump outputs
        output_backup_helper.dump_output(feedback_object, save_output, proc_stdout, ("Cmake's stdout has been saved to: [%s]" % save_output))
        output_backup_helper.dump_output(feedback_object, save_error_output, proc_stderr, ("Cmake's stderr has been saved to: [%s]" % save_error_output))

        # autobackup outputs
        output_list = [("cmake_plugin_stdout", proc_stdout, "Cmake's stdout"), ("cmake_plugin_stderr", proc_stderr, "Cmake's stderr")]
        warnings = log_helper.add_to_warnings(warnings, output_backup_helper.dump_outputs_autobackup(proc_result, feedback_object, output_list))

        # warnings
        if len(proc_stderr) > 0:
            if not suppress_stderr_warnings:
                warnings = log_helper.add_to_warnings(warnings, proc_stderr)
            else:
                warnings = log_helper.add_to_warnings(warnings, "cmake's stderr has been suppressed")
        return True, warnings
