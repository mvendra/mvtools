#!/usr/bin/env python3

import sys
import os

import path_utils
import cmake_wrapper

def boot_options():
    return {}

def set_option(options, option_name, option_type, option_value):
    if options is None:
        return None
    local_options = options.copy()
    local_options[option_name] = (option_type, option_value)
    return local_options.copy()

def set_option_parse(options, option_string):

    option_string_local = option_string

    option_name_local = None
    option_type_local = None
    option_value_local = None

    colon_pos = option_string_local.find(":")
    if colon_pos == -1:
        return None
    option_name_local = option_string_local[:colon_pos]
    option_string_local = option_string_local[colon_pos+1:]

    eq_sign_pos = option_string_local.find("=")
    if eq_sign_pos == -1:
        return None
    option_type_local = option_string_local[:eq_sign_pos]
    option_string_local = option_string_local[eq_sign_pos+1:]

    option_value_local = option_string_local

    return set_option(options, option_name_local, option_type_local, option_value_local)

def set_option_toolchain(options, option_value):
    return set_option(options, "CMAKE_TOOLCHAIN_FILE", "STRING", option_value)

def set_option_install_prefix(options, option_value):
    return set_option(options, "CMAKE_INSTALL_PREFIX", "STRING", option_value)

def configure_and_generate(cmake_path, suppress_cmake_output, source_path, output_path, generator_type, options):

    local_generator_type = generator_type

    # shortcuts / tricks
    if local_generator_type == "makefile":
        local_generator_type = "Unix Makefiles"

    return cmake_wrapper.configure_and_generate(cmake_path, suppress_cmake_output, source_path, output_path, local_generator_type, options)
